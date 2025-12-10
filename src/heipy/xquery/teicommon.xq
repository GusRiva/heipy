xquery version "3.1";

module namespace teicommon = "http://exist-db.org/xquery/teicommon";
declare namespace tei = "http://www.tei-c.org/ns/1.0";
declare namespace hei = "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS";
declare namespace mathml = "http://www.w3.org/1998/Math/MathML";
declare namespace functx = "http://www.functx.com";

(:  ToDo/Vorschlag: Bereich zwischen milestone und zugehörigem Anchor über intersect-Funktion
  
 Beispiel:
 Der folgende Ausdruck geht von einem übergebenen Kontextknoten aus und wählt alle <lb>s bis zum nächsten <cb>:
 following::cb[1]/preceding::lb intersect following::lb
 
:)

declare function teicommon:sort-document-order
  ( $seq as node()* )  as node()* {

   $seq/.
 } ;

declare function teicommon:combine-maps($A as map(*), $B as map(*)) {
    fn:fold-left(map:keys($B), $A, function($z, $k){ 
        if (map:contains($z, $k))
        then map:put($z, $k, distinct-values(($z($k), $B($k))))
        else map:put($z, $k, $B($k))
    })
};




declare function teicommon:generate_substJoin_map($node as node())
{
    let $map_substJoin2mod := map:merge(
            for $substJ in $node//tei:substJoin return (
                if ($substJ/@target) then (
                    map:entry(if ($substJ/@xml:id) then $substJ/@xml:id/string() else concat('sj-',generate-id($substJ)),tokenize(replace($substJ/@target,'#',''), '  *'))
                )
                else ()
            )
        )

    let $map_mod2substJoin := map:merge(
            for $substJ in $node//tei:substJoin return (
                if ($substJ/@target) then (
                    let $substid := if ($substJ/@xml:id) then $substJ/@xml:id/string() else concat('sj-',generate-id($substJ))
                    for $t in tokenize(replace($substJ/@target,'#',''), '  *') return
                        map:entry($t,$substid)
                )
                else ()
            )
        )
        
    return map:merge((map:entry('substJoin2mod',$map_substJoin2mod),map:entry('mod2substJoin',$map_mod2substJoin)))
};


declare function teicommon:missing_substJoin_elements($node as node()*,$all as node()*, $func, $rendering)
{
    (: Einfügen von substJoin-Elemente, die nicht in $node aber in $all enthalten sind (die also außerhalb des gewählten Ausschnitts liegen) :)    
    if (map:contains($rendering,'substJoin-map')) then
        if (map:contains(map:get($rendering,'substJoin-map'),'mod2substJoin') and map:contains(map:get($rendering,'substJoin-map'),'substJoin2mod')) then (
            let $s := map:merge(
                for $n in ($node//tei:add[@xml:id],$node//tei:del[@xml:id]) return
                    if (map:contains(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$n/@xml:id/string())) then map:entry(map:get(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$n/@xml:id/string()),1)
                    else ()
                )
            for $k in (map:keys($s)) return
                for $e in (map:get(map:get(map:get($rendering,'substJoin-map'),'substJoin2mod'),$k)) return 
                    if ($node//*[@xml:id eq $e]) then ()
                    else teicommon:transform-to-html($all//*[@xml:id eq $e], $func, $rendering)
        )
        else ()
    else ()
    
};

declare function teicommon:copy_id($node as node(),$rendering)
{
    let $ret :=
        if ($node/@xml:id) then (
            if (map:contains($rendering,'transpose-id')) then (
                attribute data-copy-of-id { $node/@xml:id }(:,:)
                (:if (teicommon:get_transpose_id($rendering, $node/@xml:id)) then attribute data-trans-id { map:get($rendering,'transpose-id') } else ():)
            )
            else
                attribute id { $node/@xml:id },
            if (teicommon:get_transpose_id($rendering, $node/@xml:id)) then attribute data-trans-id { teicommon:get_transpose_id($rendering, $node/@xml:id) } else ()
        )
        else ()  
    return $ret
};

declare function teicommon:generate_transpose_map($node as node())
{
    let $map_aut := map:merge(
            for $tr in $node//tei:transpose return (
                let $transid := if ($tr/@xml:id) then $tr/@xml:id/string() else concat('tr-',generate-id($tr))
                let $newnodes := for $x in $tr/tei:ptr/@target return $node//*[@xml:id eq replace($x,'#','')] (: ToDo: Unterstützung von range-Angabe :)
                let $new := for $x in $newnodes return string($x/@xml:id)
                let $orig := teicommon:sort-document-order($newnodes)
                for $t in $tr/tei:ptr/@target
                    return
                        map:entry(
                            replace($t,'#',''),
                            map:merge(map:entry('aut',map:merge((map:entry('id', $transid), map:entry('new', $new), map:entry('pos',index-of($orig/@xml:id,replace($t,'#','')))))))
                        )  
            )
        )
        
    let $map_ed := map:merge(
            for $tr in $node//tei:link[@ana eq "hc:EditorialTransposition"] return (
                let $transid := if ($tr/@xml:id) then $tr/@xml:id/string() else concat('tr-',generate-id($tr))
                let $newnodes := for $x in tokenize(replace($tr/@target,'#',''),'  *') return $node//*[@xml:id eq $x] (: ToDo: Unterstützung von range-Angabe :)
                let $new :=for $x in $newnodes return string($x/@xml:id)
                let $orig := teicommon:sort-document-order($newnodes)
                for $t in tokenize(replace($tr/@target,'#',''),'  *')
                    return
                        map:entry(
                            replace($t,'#',''),
                            map:merge(map:entry('edt',map:merge((map:entry('id', $transid), map:entry('new', $new), map:entry('pos',index-of($orig/@xml:id,replace($t,'#','')))))))
                        )
            )
        )
    let $map := map:merge(($map_aut, $map_ed))
    return $map
};

declare function teicommon:is_transpose($rendering,$id)
{
    let $ret :=
        if (map:contains($rendering,'transpose-map')) then
            if (map:contains(map:get($rendering,'transpose-map'),$id)) then (
                if (map:contains(map:get(map:get($rendering,'transpose-map'),$id),'edt')) then 'edt'
                else 'aut'
            )
            else ''
        else ''
    return $ret
};

declare function teicommon:get_transpose_id($rendering,$id)
{
    let $ret :=
        if (map:contains($rendering,'transpose-map')) then
            if (map:contains(map:get($rendering,'transpose-map'),$id)) then (
                for $t in map:keys(map:get(map:get($rendering,'transpose-map'),$id))
                    return map:get(map:get(map:get(map:get($rendering,'transpose-map'),$id),$t),'id')
            )
            else ()
        else ()
    return string-join($ret, ' ')
};

declare function teicommon:get_transposed($rendering,$id)
{
    let $type := teicommon:is_transpose($rendering,$id)
    let $ret := 
        if ($type) then (
            let $pos := map:get(map:get(map:get(map:get($rendering,'transpose-map'),$id),$type),'pos')
            return map:get(map:get(map:get(map:get($rendering,'transpose-map'),$id),$type),'new')[$pos]
        )
        else ''
    return $ret
};

declare function teicommon:transposed_element($node,$rendering)
{
    let $ret := $node/ancestor::tei:TEI//*[@xml:id eq teicommon:get_transposed($rendering,$node/@xml:id/string())]/self::node()
    return $ret
};

declare function teicommon:process_transposed_element_html($node,$func,$rendering)
{
    let $ret := 
        if ($node/@xml:id and not(map:contains($rendering,'transpose-id')) and teicommon:is_transpose($rendering,$node/@xml:id/string())) then (
            teicommon:transform-to-html(
                teicommon:transposed_element($node,$rendering),
                $func,
                map:put(map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string())),concat('transposed-',teicommon:is_transpose($rendering,$node/@xml:id/string())),'yes')
            )
        )
        else ()  
    return $ret
};

declare function teicommon:show_edt_transposed_txt($node,$rendering)
as xs:boolean
{
    let $ret :=
        if (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions'))
            and map:get($rendering,'text-mode') eq 'editor')
            and $node/@xml:id
            and teicommon:is_transpose($rendering,$node/@xml:id/string()) eq 'edt'
            and not(map:contains($rendering,'transpose-id'))
        ) then true()
        else false()
    return $ret
};

declare function teicommon:show_aut_transposed_txt($node,$rendering)
as xs:boolean
(: Schreiberumstellungen werden in der Textausgabe immer nachvollzogen, unabhängig von den Einstellungen :)
{
    let $ret :=
        if ($node/@xml:id
            and teicommon:is_transpose($rendering,$node/@xml:id/string()) eq 'aut'
            and not(map:contains($rendering,'transpose-id'))
        ) then true()
        else false()
    return $ret
};

declare function teicommon:transposed_class($node,$rendering)
{
    let $ret :=
        if ($node/@xml:id and teicommon:is_transpose($rendering,$node/@xml:id/string())) then
            if (map:contains($rendering,concat('transposed-',teicommon:is_transpose($rendering,$node/@xml:id/string())))) then concat('t-trans-',teicommon:is_transpose($rendering,$node/@xml:id/string()))
            else concat('t-trans-',teicommon:is_transpose($rendering,$node/@xml:id/string()),'-orig')
        else ''
    return $ret
};

declare function teicommon:sections-no($node as node())
{
    let $c := concat(if ($node/ancestor::tei:div) then (concat(teicommon:sections-no($node/ancestor::tei:div[1]),'-')) else (),count($node/preceding-sibling::tei:div)+1)
    return $c
};

declare function teicommon:verse-no($node as node(),$test-mod5)
(: test-mod5: ggf. mod5-Klasse erzeugen :)
{
    if ($node/@n) then element div {
        attribute class {
            't-vno',
            if ($test-mod5) then (
                if (matches($node/@n,'[05]$')) then 'mod5'
                else
                    if (fn:number($node/@n)) then 
                        if (fn:number($node/preceding::tei:l[1]/@n)) then
                            if (fn:number($node/@n) != fn:number($node/preceding::tei:l[1]/@n) + 1) then 'mod5'
                            else ''
                        else ''
                    else 'mod5'
            )
            else ''
        },
        element span {string($node/@n)}
    } else (),
    if ($node/@hei:altN) then element div {
        attribute class {
            't-vno2',
            if ($test-mod5) then (
                if (matches($node/@hei:altN,'[05]$')) then 'mod5'
                else
                    if (fn:number($node/@hei:altN)) then 
                        if (fn:number($node/preceding::tei:l[1]/@hei:altN)) then
                            if (fn:number($node/@hei:altN) != fn:number($node/preceding::tei:l[1]/@hei:altN) + 1) then 'mod5'
                            else ''
                        else ''
                    else 'mod5'
            )
            else ''
        },
        element span {string($node/@hei:altN)}
    } else ()
};

declare function teicommon:contrib_id($sk)
{
    let $i := concat('contrib_',replace(normalize-space($sk),'[^A-Za-z]','_'))
    return $i
};

declare function teicommon:sortkey($n as node())
{
    let $sk :=  if ($n/tei:persName) then
                    if ($n/tei:persName[1]/tei:surname) then
                        concat($n/tei:persName[1]/tei:surname/string(), text{', '}, $n/tei:persName[1]/tei:forename/string())
                    else
                        $n/tei:persName[1]/string()
                else if ($n/tei:orgName) then
                    $n/tei:orgName[1]/string()
                else
                    $n/string()
    return $sk
    
};

declare function teicommon:contrib_type($seq as item()*)
{
    for $item in $seq
        let $ct :=
            if ($item/@ref) then substring-after($item/@ref,'relators/')
            else (
                if ($item/local-name() eq 'author') then 'aut'
                else if ($item/local-name() eq 'editor') then 'edt'
                else 'ctb'
            )
        return $ct
};

declare function teicommon:contrib_sort( $seq as item()* )  as item()* {
    for $item in $seq
        let $sort-key := teicommon:sortkey($item)
        group by $sort-key
        order by $sort-key 
        return element div {
            attribute id {teicommon:contrib_id($sort-key)},
            attribute class {'t-contrib'},
            attribute data-contrib-type {distinct-values(teicommon:contrib_type($item))},
            element div {attribute class {'t-contrib-name'}, $sort-key},
            (:element div {attribute class {'t-contrib-name-display'}, if ($item/tei:persName) then concat($item/tei:persName/tei:forename/string(),' ',$item/tei:persName/tei:surname/string()) else $item/tei:orgName/string()},:)
            element div {attribute class {'t-contrib-types'}, distinct-values(teicommon:contrib_type($item))},
            element div {
                attribute class {'t-contrib-ids'},
                if ($item/tei:idno[@ana eq 'hc:GNDURI']) then element div {'GND: ', element a {attribute href {$item/tei:idno[@ana eq 'hc:GNDURI']}, attribute class {'t-gnd-link'}, attribute target {'_blank'}, string($item/tei:idno[@ana eq 'hc:GNDURI'][1])}} else (),
                if ($item/tei:idno[@ana eq 'hc:ORCIDURI']) then element div {'ORCID: ',element a {attribute href {$item/tei:idno[@ana eq 'hc:ORCIDURI']}, attribute class {'t-orcid-link'}, attribute target {'_blank'}, string($item/tei:idno[@ana eq 'hc:ORCIDURI'][1])}} else ()
            },
            element div {attribute class {'t-contrib-affs'}, for $i in $item return teicommon:front-transform-to-html($i/tei:affiliation,'','')},
            element div {attribute class {'t-contrib-email'}, for $i in $item return teicommon:front-transform-to-html($i/tei:email,'','')}
        }
};

declare function teicommon:list_type($rendition)
{
  let $type :=
    (: ToDo: ergänzen :)
    if (contains($rendition,'hc:ItemMarkerDisc')) then ''
    else if (contains($rendition,'hc:ItemMarkerDecimal')) then ''
    else if (contains($rendition,'hc:ItemMarkerLowerRoman')) then 't-list-lower-roman'
    else ''
  return $type
};

declare function teicommon:output-line($c, $lno, $linetext)
as item ()*
{
    let $t :=
        element div {
            attribute class { $c },
            element div { attribute class { "t-vno"}, ''},
            element div { attribute class { "t-vno2"}, ''}, 
            element div { attribute class { "t-lno", if (matches($lno,'^[0-9]*[05]$')) then 'mod5' else (if (matches($lno,'^Tab')) then 'mod5tab' else ())}, if ($lno) then element span { $lno } else () },
            element div { attribute class { "t-func" }},
            $linetext
        }
    return $t
};

declare function teicommon:gap($node as node())
as item()*
{
    let $t := (
            (: ToDo nach Konvertierung aller Editionen sollte nur noch @unit line/character übrig bleiben :)
            attribute class {
                if ($node/@ana eq "hc:PassiveSynopticGap") then 't-gap-passive'
                else if ($node/@unit eq "leafs" or $node/@unit eq "leaf") then 't-gap-leaf'
                else if ($node/@unit eq "pages" or $node/@unit eq "page") then 't-gap-page'
                else if ($node/@unit eq "lines" or $node/@unit eq "line") then 't-gap-line'
                else if ($node/@unit eq "char" or $node/@unit eq "chars" or $node/@unit eq "character" or $node/@unit eq "characters") then 't-gap-character'
                else if ($node/@unit) then concat('t-gap-',string($node/@unit)) else 't-gap-unknown',
                
                if ($node/tei:certainty) then 't-gap-unsure' else '',
            
                (: @rendition :)
                if ($node/@rendition) then teicommon:rendition2class($node) else ''
            },
            if ($node/@agent) then attribute data-agent { string($node/@agent) } else (),
            if ($node/@reason) then attribute data-reason { string($node/@reason) } else (),
            if ($node/@extent) then attribute data-extent {string($node/@extent)} else (attribute data-extent { "not stated" }),
            if ($node/@quantity) then attribute data-quantity {string($node/@quantity)} else (attribute data-quantity { "not stated" }),
            if ($node/@atLeast) then attribute data-at-least { string($node/@atLeast) } else (),
            if ($node/@atMost) then attribute data-at-most { string($node/@atMost) } else (),
            if ($node/@precision) then attribute data-precision { string($node/@precision) } else (),
        
            if ($node/child::tei:desc) then attribute data-desc { replace(string($node/tei:desc),'"','&quot;') } else (),
            (: ToDo: alte Codierungen (s.o.) entfernen :)
            if ($node/@ana) then attribute data-ana { string($node/@ana) } else (),
            if ($node/@rendition) then attribute data-rend { string($node/@rendition) } else () (: data-rend zusätzlich zu Klasse für Beschreibung :)
    )
    
    return $t
};

(: 
 : ### teicommon:node2project($node) 
 : 
 : Name des Projekt(-ordner)s zu einem beliebigen TEI-Node
 : 
 :)

declare function teicommon:data-line-attr($n as node())
{
    let $r := 
        (: evtl. eXist-Bug? https://github.com/eXist-db/exist/issues/3459 :)
        if ($n/ancestor::tei:line) then attribute data-line {
            concat(if ($n/ancestor::tei:surface[1]/@n) then concat(string($n/ancestor::tei:surface[1]/@n),'.') else '', if ($n/ancestor::tei:zone[@ana='hc:Column'][1]/@n) then concat(string($n/ancestor::tei:zone[@ana='hc:Column'][1]/@n),'.') else '',string($n/ancestor::tei:line[1]/@n))
        }
        else if ($n/ancestor::tei:row) then attribute data-line {
            concat(if ($n/ancestor::tei:surface[1]/@n) then concat(string($n/ancestor::tei:surface[1]/@n),'.') else '', if ($n/ancestor::tei:zone[@ana='hc:Column'][1]/@n) then concat(string($n/ancestor::tei:zone[@ana='hc:Column'][1]/@n),'.') else '',string($n/ancestor::tei:row[1]/@n))
        }
        else if ($n/preceding::tei:lb) then attribute data-line {
            concat(if ($n/ancestor::tei:surface[1]/@n) then concat(string($n/ancestor::tei:surface[1]/@n),'.') else '', if ($n/preceding::tei:cb[1]/@n) then concat(string($n/preceding::tei:cb[1]/@n),'.') else '',string($n/preceding::tei:lb[1]/@n))
        }
        (: ToDo :)
        (:else if ($n/preceding::*[local-name() eq 'lb']) then attribute data-line {string($n/preceding::*[local-name() eq 'lb'][1]/@n)}:)
        else ()
    return $r
};


(: 
 : ### teicommon:clean-id($str) 
 : 
 : Remove from $str all '#' and replace space with colon.
 : 
 :)
declare function teicommon:clean-id($str)
{
    replace(replace(string($str), '#', ''), ' ', '__JOIN__')
};

declare function teicommon:clean-facs($str)
{
    replace(string($str),'#[^_]*_0*','')
};

declare function teicommon:facs2page($node as node(), $facs)
{
    let $n := text {if ($node/ancestor::tei:TEI/tei:facsimile/tei:surface/tei:zone[@xml:id eq substring($facs,2)]/parent::tei:surface/@n) then string($node/ancestor::tei:TEI/tei:facsimile/tei:surface/tei:zone[@xml:id eq substring($facs,2)]/parent::tei:surface/@n) else ('')}
    return $n
};

declare function teicommon:rendition2class($node as node())
{
    let $r := text { if ($node/@rendition) then replace(concat('t-rend-',string-join(tokenize($node/@rendition, ' '),' t-rend-')),':','_') else ()}
    return $r
};

declare function teicommon:ana2class($node as node(), $prefix)
{
    let $r := text { if ($node/@ana) then replace(concat($prefix,string-join(tokenize($node/@ana, ' '),concat(' ',$prefix))),':','_') else ('')}
    return $r
};

declare function teicommon:color2class($node as node())
{
    let $r := (concat('t-color-',string-join(tokenize($node/@hei:color, ' '),' t-color-')), if ($node[contains(@hei:color, ' ')]) then (concat('t-primary-color-',fn:head(tokenize($node/@hei:color, ' ')))) else ())
    return $r
};


declare function teicommon:transform-ms-identifier-to-html($nodes as node()*, $func, $rendering)
{
    let $ret := 
    for $n in ($nodes) return (
        if (local-name($n) eq "altIdentifier") then ()
        else (
            element span {
                attribute class {concat('t-',local-name($n)), if (local-name($n) eq "idno") then teicommon:ana2class($n,'t-ms-') else ''},
                if ($n/@xml:lang) then attribute lang {string($n/@xml:lang)} else (),
                if (local-name($n) eq "idno") then (
                    $n/string(),
                    if ($n/@ana eq 'hc:GNDURI') then element a {attribute class {'t-gnd-link'}, attribute href {$n/@ana eq 'hc:GNDURI'}, attribute target {'_blank'}, 'GND'} else ()
                )
                else if (local-name($n) eq "msName" or local-name($n) eq "objectName" or local-name($n) eq "note") then (
                    $n/string()
                )
                else (
                    teicommon:transform-to-html($n/tei:name, $func, $rendering),
                    teicommon:transform-to-html($n/tei:placeName, $func, $rendering),
                    teicommon:transform-to-html($n/tei:orgName, $func, $rendering),
                    if ($n/tei:idno[@ana eq 'hc:GNDURI']) then element a {attribute class {'t-gnd-link'}, attribute href {$n/tei:idno[@ana eq 'hc:GNDURI']}, attribute target {'_blank'}, 'GND'} else ()
                )
            }
        )
    )
    
    return $ret
};

(: Funktion zur Verarbeitung der Metadaten übergeordneter Elemente (beim Aufruf von Kapitel etc.) :)
declare function teicommon:front-transform-to-html($nodes as node()*, $func, $rendering)
as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case text()
                return $node
            
            case element(tei:teiHeader)
                return (
                    element div {for $n in ($node/tei:fileDesc/tei:titleStmt, $node/tei:fileDesc/tei:editionStmt, $node/tei:fileDesc/tei:publicationStmt, $node/tei:profileDesc/tei:creation, $node/tei:fileDesc/tei:sourceDesc, $node/tei:fileDesc/tei:publicationStmt/tei:listBibl, $node/tei:notesStmt (: letzteres alte Codierung, ToDO :)) return teicommon:front-transform-to-html($n, $func, $rendering)}
                )
                
            case element(tei:titleStmt)
                return (
                    if ($node/tei:author and not($node/ancestor::tei:teiHeader/following-sibling::tei:text[contains(@ana,'hc:ScholarlyArticle')]))
                        then element div {attribute class {'t-contrib-group t-contrib-group-aut'}, teicommon:front-transform-to-html($node/tei:author, $func, $rendering)}
                        else (),
                    teicommon:transform-to-html($node/tei:title, $func, $rendering),
                    if (($node/tei:author and $node/ancestor::tei:teiHeader/following-sibling::tei:text[contains(@ana,'hc:ScholarlyArticle')]) or $node/tei:editor or $node/tei:respStmt)
                        then element div {attribute class {'t-contrib-group'}, if ($node/ancestor::tei:teiHeader/following-sibling::tei:text[contains(@ana,'hc:ScholarlyArticle')]) then teicommon:front-transform-to-html($node/tei:author, $func, $rendering) else (), teicommon:front-transform-to-html($node/tei:editor, $func, $rendering), teicommon:front-transform-to-html($node/tei:respStmt, $func, $rendering)}
                        else (),
                    if ($node/tei:funder) then
                        element div {attribute class {'t-funding-g t-funder-g'}, teicommon:front-transform-to-html($node/tei:funder, $func, $rendering)}
                    else (),
                    if ($node/tei:sponsor) then
                        element div {attribute class {'t-funding-g t-sponsor-g'}, teicommon:front-transform-to-html($node/tei:sponsor, $func, $rendering)}
                    else ()
                )
            
            case element(tei:editionStmt)
                return element div {attribute class {'t-edition'}, teicommon:front-transform-to-html($node/tei:edition, $func, $rendering)}
            
            case element(tei:sourceDesc)
                return element div {
                    attribute class {'t-sourcedesc'},
                    teicommon:front-transform-to-html($node/*, $func, $rendering) (: nur Sub-Tags verarbeiten, keine Textknoten, damit t-sourcedesc ggf. leer ist und per CSS ausgeblendet werden kann. :)
                }
            
            case element(tei:publicationStmt)
                return (
                    element div {
                        attribute class {'t-publication'},
                        if ($node/tei:pubPlace) then (
                            teicommon:front-transform-to-html($node/tei:pubPlace, $func, $rendering)
                        )
                        else (),
                        if ($node/tei:publisher) then (
                            if ($node/tei:pubPlace) then ': ' else '',
                            teicommon:front-transform-to-html($node/tei:publisher, $func, $rendering)
                        )
                        else (),                        
                        if ($node/tei:date) then (
                            if ($node/tei:publisher or $node/tei:pubPlace) then ', ' else '',
                            $node/tei:date/string()
                        )
                        else ()
                    },
                    teicommon:front-transform-to-html($node/tei:availability, $func, $rendering),
                    if ($node/tei:idno[@ana eq 'hc:DOI']) then (element div {attribute class {'t-doi'}, element span {'DOI: '}, element a {attribute href {$node/tei:idno[@ana eq 'hc:DOI']/text()}, $node/tei:idno[@ana eq 'hc:DOI']/text()}}) else ()(:),
                    ToDo: Wo ist ISSN etc untergebracht?
                    if ($node/tei:idno[@ana eq 'hc:ISSN']) then (element div {attribute class {'t-isbn'}, element span {'ISSN: '}, element a {attribute href {$node/tei:idno[@ana eq 'hc:ISSN']/text()}, $node/tei:idno[@ana eq 'hc:ISSN']/text()}}) else ():)
                )
            case element(tei:notesStmt)
                return (
                    for $n in ($node/tei:note) return
                        element div {
                            attribute class {'t-notes'},
                            if ($n/@xml:lang) then attribute lang {string($n/@xml:lang)} else (),
                            teicommon:transform-to-html($n, $func, $rendering)
                        }
                )
                
            case element(tei:msDesc)
                return if ($node/*[not(local-name() eq 'physDesc')]) then element div {attribute class {'t-msdesc'}, teicommon:front-transform-to-html($node/node(), $func, $rendering)} else ()
                
            case element(tei:additional)
                return teicommon:front-transform-to-html($node/node(), $func, $rendering)
                
            case element(tei:surrogates)
                return element div {attribute class {'t-surrogates'}, teicommon:front-transform-to-html($node/tei:listBibl, $func, $rendering)}
                
            case element(tei:creation)
                return (
                    if ($node/tei:origPlace or $node/tei:origDate) then
                        element div {
                            attribute class {'t-creation'},
                            if ($node/tei:origPlace) then element div {element span {attribute lang {'de'}, 'Entstehungsort'}, element span {attribute lang {'en'}, 'Place of origin'}, ': ', teicommon:transform-to-html($node/tei:origPlace/tei:placeName, $func, $rendering)} else (),
                            if ($node/tei:origDate) then element div {element span {attribute lang {'de'}, 'Entstehungsdatum'}, element span {attribute lang {'en'}, 'Date of origin'}, ': ', teicommon:transform-to-html($node/tei:origDate, $func, $rendering)} else ()
                        }
                    else ()
                )
                
            case element(tei:msIdentifier)
                return (
                    element div {
                        attribute class {'t-ms-identifier'},
                        teicommon:transform-ms-identifier-to-html($node/element(), $func, $rendering)
                    },
                    for $a in ($node/tei:altIdentifier) return (
                        element div {
                            attribute class {'t-ms-alt-identifier'},
                            teicommon:transform-ms-identifier-to-html($a/element(), $func, $rendering)
                        }
                    )
                )
            
            case element(tei:seriesStmt)
                return (
                    element div {
                            attribute class {'t-meta-collection'},
                            element div {
                                if ($node/tei:title) then element div {
                                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                                    attribute class {'t-title'}, string($node/tei:title)
                                } else (),
                                if ($node/tei:biblScope[@unit eq 'volume']) then element div {attribute class {'t-vol'}, string($node/tei:biblScope[@unit eq 'volume'])} else ()
                            }
                            (: ToDo: Beiträger :)
                    }
                )
                
            case element(tei:monogr)
                return (
                    if ($node/tei:title[@level eq 'j']) then
                        element div {
                            attribute class {'t-meta-journal'},
                            
                            (: ZS-Titel :)
                            element div {attribute class {'t-title'}, string($node/tei:title[@level='j'][1])},
                            
                            (: Band, Heft, Jahr :)
                            if ($node/tei:imprint) then (
                                element div {
                                    attribute class {'t-issue'},
                                    if ($node/tei:imprint/tei:biblScope[@unit eq 'volume']) then string($node/tei:imprint/tei:biblScope[@unit eq 'volume']) else '',
                                    if ($node/tei:imprint/tei:date) then (concat('(', normalize-space($node/tei:imprint/tei:date),')')) else '',
                                    if ($node/tei:imprint/tei:biblScope[@unit eq 'issue']) then (
                                        if ($node/tei:imprint/tei:biblScope[@unit eq 'volume'] or $node/tei:imprint/tei:date) then ', ' else '',
                                        string ($node/tei:imprint/tei:biblScope[@unit eq 'issue'])
                                    ) else ()
                                }
                            )
                            else (),
                            
                            (: ISSN/ISBN :)
                            for $n at $pos in ($node/tei:idno[contains(@ana,'hc:ISSN') or contains(@ana,'hc:ISBN')]) return (
                                    element div {attribute class {'t-isbn', if ($pos = 1) then 't-isbn-first' else ''}, element span {if (contains($n/@ana,'hc:ISSN')) then 'ISSN: ' else 'ISBN: ', $n/text()}}
                            )
                        }
                    else ()
                )

            case element(tei:pubPlace)
                return (element span {attribute class {'t-publication-place'}, attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])}, teicommon:transform-to-html($node/tei:placeName, $func, $rendering)})
                
            case element(tei:publisher)
                return (element span {attribute class {'t-publisher'}, attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])}, teicommon:transform-to-html($node/tei:orgName, $func, $rendering)})
            
            case element(tei:listBibl)
                return (
                    if ($node/parent::tei:publicationStmt) then
                        element div {teicommon:front-transform-to-html($node/node(), $func, $rendering)}
                    else
                        element ul {teicommon:front-transform-to-html($node/node(), $func, $rendering)}
                )
                
            case element(tei:bibl)
                return (
                    if ($node/parent::tei:listBibl and not($node/ancestor::tei:publicationStmt)) then
                        element li {
                            if ($node/@xml:lang) then attribute lang {string($node/@xml:lang)} else (),
                            attribute class {
                                if (contains($node/@ana,'hc:RecommendedBibliographicReference')) then 't-cite' else '',
                                if ($node/@ana) then teicommon:ana2class($node,'t-bibl-') else ''
                            },
                            teicommon:transform-to-html($node/node(), $func, $rendering)
                        }
                    else
                        element div {
                            if ($node/@xml:lang) then attribute lang {string($node/@xml:lang)} else (),
                            attribute class { 
                                (: direkt in sourceDesc: Zitierempfehlung :)
                                if ($node/parent::tei:sourceDesc) then 't-cite' else '',
                                if (contains($node/@ana,'hc:RecommendedBibliographicReference')) then 't-cite' else '',
                                if ($node/@ana) then teicommon:ana2class($node,'t-bibl-') else ''
                            },
                            teicommon:transform-to-html($node/node(), $func, $rendering)
                        }
                )
            
            case element(tei:funder)
                return element div {
                    attribute class {'t-funding-s'},
                    if ($node/tei:idno[@ana eq 'hc:GNDURI']) then attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])} else (),
                    if ($node/tei:idno[@ana eq 'hc:ORCIDURI']) then attribute data-orcid {string($node/tei:idno[@ana eq 'hc:ORCIDURI'])} else (),
                    for $n in ($node/node()) return
                        if (local-name($n) ne 'idno') then teicommon:transform-to-html($n, $func, $rendering)
                        else ()
                }
                
            case element(tei:sponsor)
                return element div {
                    attribute class {'t-funding-s'},
                    if ($node/tei:idno[@ana eq 'hc:GNDURI']) then attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])} else (),
                    if ($node/tei:idno[@ana eq 'hc:ORCIDURI']) then attribute data-orcid {string($node/tei:idno[@ana eq 'hc:ORCIDURI'])} else (),
                    for $n in ($node/node()) return
                        if (local-name($n) ne 'idno') then teicommon:transform-to-html($n, $func, $rendering)
                        else ()
                }
                
            case element(tei:author)
                return (
                    if ($node/tei:note) then element span {attribute class {'t-contrib-note'}, concat($node/tei:note/string(),' ')} else (),
                    element span {
                        attribute data-target {teicommon:contrib_id(teicommon:sortkey($node))},
                        attribute class {'t-contrib-name'},
                        if ($node/tei:idno[@ana eq 'hc:GNDURI']) then attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])} else (),
                        if ($node/tei:idno[@ana eq 'hc:ORCIDURI']) then attribute data-orcid {string($node/tei:idno[@ana eq 'hc:ORCIDURI'])} else (),
                        attribute data-contrib-type {teicommon:contrib_type($node)},
                        if ($node/tei:persName or $node/tei:orgName) then
                            normalize-space(concat($node/tei:persName[1]/string(),$node/tei:orgName[1]/string()))
                        else
                            normalize-space($node/string())
                    }
                )
                
            case element(tei:editor)
                return (
                    if ($node/tei:note) then element span {attribute class {'t-contrib-note'}, concat($node/tei:note/string(),' ')} else (),
                    element span {
                        attribute data-target {teicommon:contrib_id(teicommon:sortkey($node))},
                        attribute class {'t-contrib-name'},
                        if ($node/tei:idno[@ana eq 'hc:GNDURI']) then attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])} else (),
                        if ($node/tei:idno[@ana eq 'hc:ORCIDURI']) then attribute data-orcid {string($node/tei:idno[@ana eq 'hc:ORCIDURI'])} else (),
                        attribute data-contrib-type {teicommon:contrib_type($node)},
                        if ($node/tei:persName or $node/tei:orgName) then
                            normalize-space(concat($node/tei:persName[1]/string(),$node/tei:orgName[1]/string()))
                        else
                            normalize-space($node/string())
                    }
                )
                
            case element(tei:respStmt)
                return (
                    if ($node/tei:note) then element span {attribute class {'t-contrib-note'}, concat($node/tei:note/string(),' ')} else (),
                    element span {
                        attribute data-target {teicommon:contrib_id(teicommon:sortkey($node))},
                        attribute class {'t-contrib-name'},
                        if ($node/tei:idno[@ana eq 'hc:GNDURI']) then attribute data-gndid {string($node/tei:idno[@ana eq 'hc:GNDURI'])} else (),
                        if ($node/tei:idno[@an eq 'hc:ORCIDURI']) then attribute data-orcid {string($node/tei:idno[@ana eq 'hc:ORCIDURI'])} else (),
                        attribute data-contrib-type {teicommon:contrib_type($node)},
                        if ($node/tei:persName or $node/tei:orgName) then
                            normalize-space(concat($node/tei:persName[1]/string(),$node/tei:orgName[1]/string()))
                        else
                            normalize-space($node/string()),
                        teicommon:front-transform-to-html($node/tei:resp, $func, $rendering)
                    }
                )
                
            case element(tei:resp)
                return element span {
                    attribute class {'t-resp'},
                    if ($node/@xml:lang) then attribute lang {string($node/@xml:lang)} else (),
                    normalize-space($node/string())
                }
            
            case element(tei:affiliation)
                return element div {
                    attribute class {'t-contrib-aff'},
                    if ($node/*) then (
                        teicommon:transform-to-html($node/tei:orgName, $func, $rendering),
                        teicommon:transform-to-html($node/tei:placeName, $func, $rendering),
                        teicommon:transform-to-html($node/tei:name, $func, $rendering)
                    )
                    else string($node),
                    if ($node/tei:idno[@ana eq 'hc:GNDURI']) then element a {attribute class {'t-gnd-link'}, attribute href {$node/tei:idno[@ana eq 'hc:GNDURI']}, attribute target {'_blank'}, 'GND'} else ()
                }
                
            case element(tei:email)
                return element a {attribute href {concat('mailto:',$node/text())}, $node/node()}
                
            case element(tei:availability) return (
                teicommon:front-transform-to-html($node/tei:licence, $func, $rendering),
                for $n in ($node/tei:p) return (
                    element div {
                        attribute class {'t-copyright'},
                        if ($n/@xml:lang) then attribute lang {string($n/@xml:lang)} else (),
                        teicommon:front-transform-to-html($n/node(), $func, $rendering)
                    }
                )
            )
            
            case element(tei:licence) return
                for $n in ($node/tei:p) return (
                    element div {
                        attribute class {'t-license'},
                        if ($n/@xml:lang) then attribute lang {string($n/@xml:lang)} else (),
                        if ($n/parent::tei:licence/@target) then
                            element div {attribute class {'t-license-img'}, attribute data-uri {$n/parent::tei:licence/@target}, element a {attribute href {$n/parent::tei:licence/@target}, attribute target {'_blank'}}}
                        else (),
                        element div {attribute class {'t-license-text'}, teicommon:front-transform-to-html($n/node(), $func, $rendering)}
                    }
                )
            
            case element(tei:ref)
                return teicommon:transform-to-html($node, $func, $rendering) (: verarbeite analog zu tei:ref in Text :)
            
            case element(tei:p)
                return teicommon:front-transform-to-html($node/node(), $func, $rendering)
            
            default return ()
};


(:~
 : ### teicommon:transform-to-html($nodes as node()*, $func, $rendering)
 : 
 : - @param $nodes nodes to transform
 : - @param $func 'verse' if output should be verse-oriented
 : - @param $rendering Whether to insert whitespace, for Nepalica
 : 
 : 
 :)
declare function teicommon:transform-to-html($nodes as node()*, $func, $rendering)
as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case text()
                return
                    if ($func eq 'page' and $node/preceding::tei:milestone[@resp eq 'hc:Editor'][1]) then
                        if ($node/following::*[1][local-name()='anchor'][@xml:id eq substring($node/preceding::tei:milestone[@resp eq 'hc:Editor'][1]/@corresp,2)]) then element span {attribute class {'t-head-edt'}, $node}
                        else $node
                    else $node

            case comment()
                return text { '' }

            (: Absätze, Kapitel, Überschriften etc. :)
            case element(tei:ab) return
                element div {
                    attribute class { "t-ab" },
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:front) return
                element div {
                    if ($node/@ana) then attribute class {'t-pubpart', teicommon:ana2class($node,'t-div-')} else (),
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    (:if ($node/@ana eq 'hc:Book' or $node/@ana eq 'hc:Chapter' or $node/@ana eq 'hc:Part' or $node/@ana eq 'hc:Section') then (
                        attribute id {concat('part-',teicommon:sections-no($node))}
                    ) else (),:)
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else ()
                    ) else (),
                    attribute data-sec-level {1},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:back) return
                element div {
                    if ($node/@ana) then attribute class {'t-pubpart', teicommon:ana2class($node,'t-div-')} else (),
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    (:if ($node/@ana eq 'hc:Book' or $node/@ana eq 'hc:Chapter' or $node/@ana eq 'hc:Part' or $node/@ana eq 'hc:Section') then (
                        attribute id {concat('part-',teicommon:sections-no($node))}
                    ) else (),:)
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else ()
                    ) else (),
                    attribute data-sec-level {1},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:div) return
                element div {
                    if ($node/@ana) then attribute class {'t-pubpart', teicommon:ana2class($node,'t-div-')} else (),
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    (:if ($node/@ana eq 'hc:Book' or $node/@ana eq 'hc:Chapter' or $node/@ana eq 'hc:Part' or $node/@ana eq 'hc:Section') then (
                        attribute id {concat('part-',teicommon:sections-no($node))}
                    ) else (),:)
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else ()
                    ) else (),
                    if (contains($node/@ana, 'hc:Section')) then (
                        attribute data-sec-level {count($node/ancestor::tei:div[@ana eq 'hc:Section'])+count($node/ancestor::tei:front)+count($node/ancestor::tei:back)+1}
                    ) else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:stage) return
                element div {
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    attribute class {'t-stage'},
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else ()
                    ) else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:sp) return
                element div {
                    if ($node/@n) then attribute data-n {string($node/@n)} else (),
                    attribute class {'t-sp'},
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else ()
                    ) else (),
                    element div {
                        attribute class {'t-speaker'}, teicommon:transform-to-html($node/tei:speaker, $func, $rendering)
                    },
                    element div {
                        attribute class {'t-speech'},  teicommon:transform-to-html($node/*[local-name() ne 'speaker'], $func, $rendering)
                    }
                }   

            (: head kommt zusätzlich als Tabellen- oder Listenüberschrift oder Bildunterschrift vor :)
            case element(tei:head) return
                if ($node/ancestor::tei:table) then element caption {teicommon:transform-to-html($node/node(), $func, $rendering)}
                else if ($node/ancestor::tei:list) then () (: wird bei tei:list mit ausgewertet :)
                else if ($node/ancestor::tei:figure) then teicommon:transform-to-html($node/node(), $func, $rendering)
                else (
                    element div {
                        attribute class { if ($node/@resp eq 'hc:Editor' (: ToDo: @resp hier veraltet :) or $node/@ana eq 'hc:EditorialContent') then "t-head-edt" else "t-head" },
                        if ($node/@xml:lang) then (attribute lang {string($node/@xml:lang)}) else (),
                        (:if ($func eq "synoptic" and $node/preceding-sibling::tei:linkGrp[@target eq concat('#',$node/@xml:id)]) then attribute data-syn-handle {'y'} else (),:)
                        (: @n des übergeordneten Elements als label übernehmen, aber nur, wenn sich Inhalt vom aktuellen Tag-Inhalt unterscheidet :)
                        if ($node/parent::tei:div/@n and ($node/string() ne string($node/parent::tei:div/@n))) then element span {attribute class {'t-label-edt'}, string($node/parent::tei:div/@n)} else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                )
            
            (: Hervorhebungen :)

            case element(tei:hi) return
                element span {
                    if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                    (: ToDo old: Codierung Initialen entfernen :)
                    attribute class { 
                        (: @rendition :)
                        teicommon:rendition2class($node), 
                        (: @hei:color :)
                        if ($node/@hei:color) then (teicommon:color2class($node)) else (),
                        (: ToDo old: @rend :)
                        if ($node[contains(@rend,'initial')]) then ('t-initial') else (),
                        if ($node/@rend) then replace(concat('tei-t-', string-join(tokenize($node/@rend, ' '),' tei-t-')),':','_') else () (: alte Codierung ??? :)
                    },
                    (: ToDo old @style (z.B. in KCD) :)
                    if ($node/@style) then attribute data-style {string($node/@style)} else (),
                    (: ToDo @n ist alte Codierung :)
                    if ($node/@n) then (attribute data-heightlines {string($node/@n)}) else (),
                    if ($node[contains(@rend,'initial')] and $node[contains(@style,'lombard')]) then attribute data-ana {'hc:Lombard'} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(hei:initial) return
                element span {
                    if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                    attribute class {
                        't-initial',
                        if ($node/@hei:color) then (teicommon:color2class($node)) else ()
                    },
                    (: ToDo: Angabe @ana deprecated, ersetzt durch @rendition, kann nach Neuerstellung KCD entfernt werden :)
                    if ($node/@ana or $node/@rendition) then attribute data-rend {concat($node/@ana,$node/@rendition)} else (),
                    if ($node/@hei:heightLines) then attribute data-heightlines {string($node/@hei:heightLines)} else (),
                    if ($node/@hei:indents) then attribute data-indents {string($node/@hei:indents)} else (),
                    if ($node/@hei:level) then attribute data-level {string($node/@hei:level)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:abbr) return (
                element span {
                    attribute class {'t-abbr', if (not($node/parent::tei:choice)) then 't-abbr-solo' else ''},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            )
            
            case element(tei:expan) return
                element span {
                    attribute class {'t-expan', if ($node/parent::tei:choice and $node/preceding-sibling::*[1][local-name() eq 'expan']) then 't-expan-2' else ''}, teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            
            case element(tei:am) return
                element span {attribute class {'t-am'}, teicommon:transform-to-html($node/node(), $func, $rendering)}
                
            case element(tei:ex) return
                element span {
                    attribute class {'t-ex', if ($node/parent::tei:choice and $node/preceding-sibling::tei:ex) then 't-ex-2' else ''}, teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            (: weitere Abkürzungsvariante siehe tei:seg :)

            case element(tei:listBibl)
                return (element ul {attribute class {'t-bibl-list'}, teicommon:transform-to-html($node/node(), $func, $rendering)})

            case element(tei:bibl) return
                if ($node/parent::tei:listBibl) then (
                    element li {
                        element div {attribute class {'t-lit'}, element div {attribute class {'t-citation'}, teicommon:transform-to-html($node/node(), $func, $rendering)}}
                    }
                )
                else if ($node/parent::tei:item and $node/parent::tei:item/parent::tei:listBibl) then (
                    (: für Konstrukt listBibl/item/bibl* :)
                    if (contains($node/@ana, "hc:ShortBibliographicReference")) then '[' else '',
                    teicommon:transform-to-html($node/node(), $func, $rendering),
                    if (contains($node/@ana, "hc:ShortBibliographicReference")) then '] ' else ''
                )
                else (
                    (: ToDo: kommt aus dem Nepalica-Projekt, Verwendung dort falsch? Wird das noch in anderen Projekten verwendet? :)
                    element span {
                        attribute class {'t-bibl'},
                        if ($node/@corresp) then attribute data-corresp {string($node/@corresp)}
                        else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                )

(:          tei:cb sollte nur bei get_textpart vorkommen. Bei versweiser Ausgabe werden nur pb innerhalb der Verse verarbeitet.  :)
            case element(tei:cb) return
                element span {attribute class { "tei-cb", if (matches(string($node/@facs),'\-a$') or $node/@rendition eq "hc:Suppress") then ( "tei-cb-first" ) else (), if ($node/ancestor::tei:l) then 'tei-cb-in_verse' else ''}, attribute data-col {teicommon:clean-facs($node/@facs)}} (: TODO: Alter Fallunterscheidung anhand facs = ...-a entfernen :)

(:         tei:pb sollte nur bei get_textpart vorkommen. Bei versweiser Ausgabe werden nur pb innerhalb der Verse verarbeitet. :)
            case element(tei:pb) return
                element span {attribute class { "tei-pb", if ($node/ancestor::tei:l) then 'tei-pb-in_verse' else ''}, attribute data-page {teicommon:clean-facs($node/@facs)}, if ($node/@facs) then attribute data-url {$node/ancestor::tei:TEI//tei:facsimile/tei:surface[@xml:id eq substring($node/@facs,2)]/tei:graphic/@url} else (), if ($node/@n) then element span {string($node/@n)} else ()}

(:          tei:lb nur bei semantic- und synoptic-Codierung :)
            case element(tei:lb) return
                if ($func eq "verse") then teicommon:transform-to-html($node/node(), $func, $rendering)
                else (element span {
                    if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                    attribute class {
                        "t-lb",
                        teicommon:rendition2class($node),
                        if ($node/@break eq "no") then concat('t-lb-break-',string($node/@break)) else ()
                    },
                    (: data-page aus letztem pb oder milestone/@ana eq 'hc:ZoneShift', je nachdem, welches näher liegt (benötigt z.B. bei Kaiserchronik-Synopse :)
                    attribute data-page {
                        if ($node/preceding::tei:milestone[@ana eq 'hc:ZoneShift']) then (
                            if ($node/preceding::tei:pb) then (
                                if ($node/preceding::tei:pb[1]/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1] and generate-id($node/preceding::tei:pb[1]/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]) = generate-id($node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]))
                                then $node/preceding::tei:pb[1]/@n
                                else teicommon:facs2page($node,$node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]/@facs)
                            )
                            else teicommon:facs2page($node,$node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]/@facs)
                        )
                        else if ($node/preceding::tei:pb[1]/@n) then $node/preceding::tei:pb[1]/@n else ('')
                    },
                    if ($node/@n) then attribute data-n {$node/@n} else ()})

(:          tei:l nur bei semantic- und synoptic-Codierung :)
            case element(tei:l) return (
                (: Versgruppe :)
                (: ToDo: performantere Lösung suchen :)
                if ($func eq "verse") then (
                    if ($node/parent::tei:lg and not($node/preceding-sibling::tei:l)) then element div {attribute class {"t-v-group"}} else ()
                )
                else (),
                
                (: eigentlicher Vers :)
                if ($func eq "verse" or $func eq "versehybride") then
                    element div {
                        attribute class { "tei-row", if ($node//tei:rdg[1]/@type eq "transposed") then "transposed-verse" else () },
                        (:attribute data-page {if ($node/preceding::tei:pb[1]/@n) then string($node/preceding::tei:pb[1]/@n) else ()},:)
                    
                        (: Synopse aus synoptic-Sicht :)
                        if ($func eq "versehybride") then (
                            element div { 
                                attribute class { "t-vno", "mod5" },
                                element span {
                                    (: TODO: alte Codierung synoptic AHD :)
                                    if ($node/@corresp) then string($node/@corresp)
                                    else if ($node/@n) then string($node/@n)
                                    else '&#160;'
                                }
                            },
                            element div {
                                attribute class { "t-vno2", "mod5" },
                                element span {
                                    (: TODO: alte Codierung synoptic AHD :)
                                    if ($node/@corresp) then string($node/@n)
                                    else if ($node/@hei:altN) then string($node/@hei:altN)
                                    else ''
                                }
                            }
                        )
                        (: Synopse aus semantic-Sicht :)
                        else (
                            element div { 
                                attribute class { "t-vno",
                                (: ToDo Variante über @xml:id weg, wenn WGD umgearbeitet :)
                                    if ($node/@xml:id and not($node/@n)) then
                                        if (matches(fn:replace($node/@xml:id, 'v_', ''),'[05]$')) then 'mod5' else (if (fn:number(fn:replace($node/@xml:id, 'v_', ''))) then '' else 'mod5') 
                                    else
                                        if (matches($node/@n,'[05]$')) then 'mod5' else (if (fn:number($node/@n)) then '' else 'mod5')
                                },
                                element span {
                                    (: ToDo Variante über @xml:id weg, wenn WGD umgearbeitet :)
                                    if ($node/@xml:id and not($node/@n)) then fn:replace($node/@xml:id, 'v_', '')
                                    else string($node/@n)
                                }
                            },
                            element div { 
                                attribute class { "t-vno2",
                                    if (matches($node/@hei:altN,'[05]$')) then 'mod5' else (if (fn:number($node/@hei:altN)) then '' else 'mod5')
                                },
                                element span {
                                    string($node/@hei:altN)
                                }
                            }
                        ),
                    
                        element div { attribute class { "t-lno" }, ''},
                        element div { attribute class { "t-func" }, ''},
                        element div { 
                            attribute class { "tei-line", if ($node/@rend eq 'missing') then "tei-verse-missing" else () },
                            if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                            teicommon:transform-to-html($node/node(), $func, $rendering)
                        },
                        if ($func eq "versehybride" or $func eq "verse") then (
                            element div {
                                attribute class {
                                    'tei-syn-page',
                                    (: Spaltenwechsel? :)
                                    if (generate-id($node/preceding::tei:cb[1]) ne generate-id($node/preceding::tei:l[1]/preceding::tei:cb[1])) then 'tei-syn-cb' else '',
                                    (: Seitenwechsel? :)
                                    if (generate-id($node/preceding::tei:pb[1]) ne generate-id($node/preceding::tei:l[1]/preceding::tei:pb[1])) then 'tei-syn-pb' else ''
                                },
                                (: TODO: Umbau: data-page und data-url analog zu pb und nur, wenn tatsächlich Seitenwechsel :)
                                if ($node/preceding::tei:pb[1]/@n) then element span {string($node/preceding::tei:pb[1]/@n)} else ()
                            }
                        ) else ()
                    }
                else 
                    element div {
                        attribute class {
                            't-verse',
                            teicommon:transposed_class($node,$rendering),
                            if (contains($node/@ana,'hc:EditorialAdditionSpan')) then 't-in-supplied' else '',
                            if (contains($node/@ana,'hc:EditorialDeletionSpan')) then 't-in-surplus' else '',
                            if (contains($node/@ana,'hc:AdditionSpan')) then 't-in-add' else '',
                            if (contains($node/@ana,'hc:DeletionSpan')) then 't-in-del' else ''
                        },
                        teicommon:copy_id($node,$rendering),
                        (:if ($func eq "synoptic" and $node/preceding-sibling::tei:linkGrp[@target eq concat('#',$node/@xml:id)]) then attribute data-syn-handle {'y'} else (),:)
                        if ($node/@hei:revisionRef) then attribute data-revision {substring($node/@hei:revisionRef,2)} else (),
                        if ($func eq "synoptic") then () else teicommon:verse-no($node,true()),
                        element div {
                            attribute class {'t-verse-l'},
                            teicommon:transform-to-html($node/node(), $func, $rendering)
                        }
                    },
                    
                    (: Verarbeitung von transpose :)
                    teicommon:process_transposed_element_html($node, $func, $rendering)
            )

(:          tei:lg kommt bei Synopsendarstellung nicht vor, da hier nur l-Elemente übermittelt werden :)
            case element(tei:lg) return
                element div {
                    attribute class {
                        "t-v-group",
                        teicommon:transposed_class($node,$rendering),
                        if (contains($node/@ana,'hc:EditorialAdditionSpan')) then 't-in-supplied' else '',
                        if (contains($node/@ana,'hc:EditorialDeletionSpan')) then 't-in-surplus' else '',
                        if (contains($node/@ana,'hc:AdditionSpan')) then 't-in-add' else '',
                        if (contains($node/@ana,'hc:DeletionSpan')) then 't-in-del' else ''
                    },
                    if ($node/@n) then attribute data-n {$node/@n} else (),
                    if ($node/@hei:revisionRef) then attribute data-revision {substring($node/@hei:revisionRef,2)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:choice) return
                element span {
                    if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                    if ($node/@prev) then attribute data-prev { string($node/@prev) } else (),
                    if ($node/@next) then attribute data-next { string($node/@next) } else (),
                    attribute class {'tei-choice'},
                    if (map:get($rendering,'data-line')) then teicommon:data-line-attr($node) else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:desc) return
                element span {
                    attribute class {'tei-desc'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:foreign) return
                element span { 
                    attribute class {'tei-foreign'},
                    if ($node/@xml:lang) then (
                        attribute lang {$node/@xml:lang},
                        (: TODO: Weitere Sprachen? :)
                        attribute dir {if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then 'rtl' else 'ltr'}
                    ) else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:ref) return
                if (contains($node/@ana, "hc:CrossReference")) then
                    element span {
                        attribute class {'t-xref', teicommon:ana2class($node,'t-ref-')},
                        if ($node/@target) then attribute data-target {string($node/@target)} else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                else 
                    element a {
                        if ($node/@target) then attribute href {string($node/@target)} else (),
                        if (contains($node/@ana, "hc:ExternalLink")) then attribute class {'t-link-ext'} else (),
                        attribute target {'_blank'},
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }

            case element(tei:title) return
                (: Titel aus Header-Information :)
                if ($node/ancestor::tei:teiHeader) then element div {
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    attribute class {if ($node/@ana eq "hc:MainTitle" or not($node/@ana)) then 't-title' else if ($node/@ana eq "hc:Subtitle") then 't-subtitle' else ''},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                (: Werktitel-Schlagwort :)
                else element span {
                    attribute class {'t-tit'},
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }                

            case element(tei:docTitle) return
                element div {
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    attribute class {'t-doc-title'},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:trailer) return
                element div {
                    if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    attribute class {'t-trailer'},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:term) return
                element span {
                    attribute class {'t-term'},
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:label) return
                if ($node/parent::tei:item) then () (: innerhalb von tei:item wird label separat verarbeitet :)
                else if ($node/parent::tei:figure) then element span {
                    attribute class {'t-fig-label'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                (: innerhalb anderer Elemente, z.B. surface :)
                else element span {
                    attribute class {'t-label'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(hei:box) return
                element div {
                    if ($node/@hei:width) then
                        attribute style {concat('flex-basis: ',$node/@hei:width)}
                    else (),
                    attribute class { 
                        "t-box",
                        if (contains($node/@ana, "hc:HorizontalLayout")) then "t-zone-hor"
                        else if (contains($node/@ana, "hc:VerticalLayout")) then "t-zone-vert"
                        else ""(:,
                        if ($node/@hei:width) then "" else "t-zone-grow":)
                    },
                    element div {teicommon:transform-to-html($node/node(), $func, $rendering)}
                }

            case element(tei:surface) return 
                element div {
                    attribute class { "t-surface" },
                    if ($node/@n) then attribute data-n { $node/@n } else (), (: wird aktuell noch nicht visualisiert? :)
                    (: temporär bis alles in heiEDITIONS-Codierung:)
                    if ($node/tei:zone[@type eq 'column' or @ana eq 'hc:Column'][2]) then element div {attribute class {'t-zone','t-zone-hor'}, element div {teicommon:transform-to-html($node/node(), $func, $rendering)}}
                    else (teicommon:transform-to-html($node/node(), $func, $rendering)),
                    element div { attribute style { "clear: both;"} }
                }

            case element(tei:zone) return 
                (: hc:LineZone nur wegen Koordinaten. Wird bei tei:line ausgewertet :)
                if ($node/@ana eq "hc:LineZone") then (teicommon:transform-to-html($node/node(), $func, $rendering))
                else (
                    element div {
                        if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                        if ($node/@n) then attribute data-n { $node/@n } else (),
                        if ($node/@hei:width) then
                            attribute style {concat('flex-basis: ',$node/@hei:width)}
                        else (),
                        if ($node/@hei:alignedByFirstLineWith) then
                            attribute data-align-line {$node/@hei:alignedByFirstLineWith}
                        else (),
                        attribute class {
                            if ($node/@type eq 'figure') then "" else "t-zone", (: Todo: Ausnahme für tei-figure-Zonen kann weg, wenn alles in heiEDITIONS-Codierung, insbes. WGD :)
                            if (contains($node/@ana, "hc:HorizontalLayout")) then "t-zone-hor"
                            else if (contains($node/@ana, "hc:VerticalLayout")) then "t-zone-vert"
                            else if ($node/@ana) then replace(concat('t-zone-',string-join(tokenize($node/@ana, ' '),' t-zone-')),':','_')
                            else "",
                            if (    $node/@rendition eq "hc:AlignmentRight" or $node/@rendition eq "hc:AlignmentBottom") then "t-zone-end"
                            else if ($node/@rendition eq "hc:AlignmentCentered") then "t-zone-center"
                            else (),
                            if ($node/@rendition eq "hc:SelfAlignmentLeft" or $node/@rendition eq "hc:SelfAlignmentTop") then "t-zone-s-start"
                            else if ($node/@rendition eq "hc:SelfAlignmentRight" or $node/@rendition eq "hc:SelfAlignmentBottom") then "t-zone-s-end"
                            else if ($node/@rendition eq "hc:SelfAlignmentCentered") then "t-zone-s-center"
                            else (),
                            if ($node/@hei:width) then "" else "t-zone-grow"
                        },
                        if ($node/@rotate) then attribute data-rotate {string($node/@rotate)} else (),
                        element div {teicommon:transform-to-html($node/node(), $func, $rendering)}
                    }  
                )

            case element(tei:line) return
                teicommon:output-line(if ($node/@rendition) then concat('tei-row ',teicommon:rendition2class($node)) else 'tei-row',
                    (: Zeilennummer :)
                    if ($node/@n) then fn:replace(string($node/@n),'^table_','Tab. ')
                    else if ($node/@xml:id) then fn:replace(fn:replace(fn:replace(string($node/@xml:id), 'l_', ''),'^.*line_',''),'^table_','Tab. ') (: weg ? :)
                    else '',
                    
                    (: Zeileninhalt :)
                    element div {
                        attribute id {
                            if ($node/@xml:id) then (string($node/@xml:id))
                            else if ($node/@n) then concat('gen_line_', generate-id($node)) 
                            else ()
                        },
                        if ($node/@facs) then (
                            attribute data-facs-points {concat($node/ancestor::tei:TEI//tei:zone[@xml:id eq substring($node/@facs,2)]/ancestor::tei:surface[1]/@lrx,':',$node/ancestor::tei:TEI//tei:zone[@xml:id eq substring($node/@facs,2)]/@points)}, (: für sourceDoc-Codierung in Leseansicht (sourceDocFragment) :)
                            attribute data-fig {$node/ancestor::tei:TEI//tei:zone[@xml:id eq substring($node/@facs,2)]/ancestor::tei:surface[1]/@xml:id}
                        ) else (),
                        attribute class {"tei-line", 
                            if ($node/@rend) then replace(concat('tei-t-', string-join(tokenize($node/@rend, ' '), ' tei-t-')), ':', '_') 
                            else ()
                        },
                        if ($node/parent::tei:zone[@ana eq 'hc:LineZone']/@points) then 
                            (: für Quellenansicht :)
                            if ($node/ancestor::tei:surface[1]/@lrx) then attribute data-points {concat($node/ancestor::tei:surface[1]/@lrx,':',$node/parent::tei:zone[@ana eq 'hc:LineZone']/@points)} else ()
                        else (),
                        if (contains($node/@ana,'hc:RunOverBelow')) then (element span {attribute class {'t-line-below'}})
                        else if (contains($node/@ana,'hc:RunOverAbove')) then (element span {attribute class {'t-line-above'}})
                        else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    })

            case element(tei:milestone) return
                (: Book :)
                if ($node/@ana eq "hc:Book" or $node/@unit eq "book") then (:ToDo: @unit wird zukünftig nicht mehr verwendet :)
                    element span { attribute class {"t-ms-Book"}, element span {string($node/@n)}}
                (: Chapter :)
                else if ($node/@ana eq "hc:Chapter" or $node/@unit eq "chapter") then ( (: ToDo: @unit wird zukünftig nicht mehr verwendet :)
                    element span { attribute class {"t-ms-Chapter"}, element span {string($node/@n)}}
                )
                (: Subchapter :)
                else if ($node/@ana eq "hc:Subchapter") then (
                    element span { attribute class {"t-ms-Subchapter"}, element span {string($node/@n)}}
                )
                (: Section :)
                else if ($node/@ana eq "hc:Section" or $node/@unit eq "section") then (: ToDo: @unit wird zukünftig nicht mehr verwendet :)
                    element span { attribute class {"t-ms-Section"}} 
                (: Heading :)
                else if ($node/@ana eq "hc:Heading") then
                    element span { 
                        if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                        attribute data-spanto {$node/@spanTo},
                        attribute class {'t-ms-head'}
                    }
                    
                (: Zeilenwechsel :)
                else if ($node/@ana eq "hc:LineSegmentBeginning") then 
                    element span {
                        if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                        attribute class {
                            "t-lb",
                            if ($node/@break eq "no") then concat('t-lb-break-',string($node/@break)) else ()
                        },
                        (: data-page aus letztem pb oder milestone/@ana eq 'hc:ZoneShift', je nachdem, welches näher liegt (benötigt z.B. bei Kaiserchronik-Synopse :)
                        attribute data-page {
                            if ($node/preceding::tei:milestone[@ana eq 'hc:ZoneShift']) then (
                                if ($node/preceding::tei:pb) then (
                                    if ($node/preceding::tei:pb[1]/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1] and generate-id($node/preceding::tei:pb[1]/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]) = generate-id($node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]))
                                    then $node/preceding::tei:pb[1]/@n
                                    else teicommon:facs2page($node,$node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]/@facs)
                                )
                                else teicommon:facs2page($node,$node/preceding::tei:milestone[@ana eq 'hc:ZoneShift'][1]/@facs)
                            )
                            else if ($node/preceding::tei:pb[1]/@n) then $node/preceding::tei:pb[1]/@n else ('')
                        },
                        if ($node/@n) then attribute data-n {$node/@n} else ()
                    }
                
                (: Verse :)
                (: ToDo: alte Codierung :)
                else if ($node/@unit eq "verse" and $node/following-sibling::*[1]/name() ne 'line') then (
                    element span { attribute class { "t-vno" }, element span { string($node/@n) }},
                    if ($node/@corresp) then element span { attribute class { "t-vno2" }, element span { string($node/@corresp) }} else ()
                )
                else if ($node/@ana eq "hc:Verse") then (
                    element span { 
                        teicommon:copy_id($node,$rendering),
                        attribute class {
                            "t-ms-Verse",
                            teicommon:transposed_class($node,$rendering)
                        },
                        element span { string($node/@n) }
                    },
                    if ($node/@hei:altN) then 
                        element span {
                            attribute class {
                                "t-ms-Verse2"
                            },
                            element span {string($node/@hei:altN)}
                        }
                    else (),
                    
                    (: Verarbeitung von transpose :)
                    teicommon:process_transposed_element_html($node, $func, $rendering)
                )
                
                
               
                (: Verspaar/-gruppe :)
                (: ToDo: alte Codierung :)
                else if ($node/@unit eq "couplet" or $node/@unit eq "quatrain" or $node/@ana eq "hc:VerseGroup") then
                    element span { attribute class { "t-ms-hc_VerseGroup" }, element span { string($node/@n) }}
                
                (: sonst :)
                else if ($node/@ana) 
                    then element span {
                        attribute class {teicommon:ana2class($node,'t-ms-')},
                        if ($node/@corresp) then attribute data-spanto {$node/@corresp} (: corresp wird verwendet, wenn anchor auch vor milestone sein kann :)
                        else if ($node/@spanTo) then attribute data-spanto {$node/@spanTo}
                        else (),
                        if ($node/@ref) then (attribute data-ref {string($node/@ref)}) else ()
                    }
                else ()
            
            case element(tei:anchor) return
                (: Attribute des zugehörigen Milestones werden teilweise kopiert :)
                element span {
                    attribute class {
                        "t-anchor",
                        if ($node/@xml:id) then (
                            if ($node/ancestor::tei:TEI[1]//tei:milestone[@corresp eq concat('#',$node/@xml:id)]) then teicommon:ana2class($node/ancestor::tei:TEI[1]//tei:milestone[@corresp eq concat('#',$node/@xml:id)],'t-anchor-')
                            else if ($node/ancestor::tei:TEI[1]//tei:milestone[@spanTo eq concat('#',$node/@xml:id)]) then teicommon:ana2class($node/ancestor::tei:TEI[1]//tei:milestone[@spanTo eq concat('#',$node/@xml:id)],'t-anchor-')
                            else if ($node/ancestor::tei:TEI[1]//tei:addSpan[@corresp eq concat('#',$node/@xml:id)]) then 't-anchor-hc_AdditionSpan'
                            else if ($node/ancestor::tei:TEI[1]//tei:addSpan[@spanTo eq concat('#',$node/@xml:id)]) then 't-anchor-hc_AdditionSpan'
                            else if ($node/ancestor::tei:TEI[1]//tei:delSpan[@corresp eq concat('#',$node/@xml:id)]) then 't-anchor-hc_DeletionSpan'
                            else if ($node/ancestor::tei:TEI[1]//tei:delSpan[@spanTo eq concat('#',$node/@xml:id)]) then 't-anchor-hc_DeletionSpan'
                            else ()
                        ) else ()
                    },
                    attribute id { $node/@xml:id },
                    if ($node/@xml:id) then attribute data-ref {$node/ancestor::tei:sourceDoc[1]//tei:milestone[@corresp eq concat('#',$node/@xml:id)]/@ref} else ()
                }

            (:  Modifikationen :)
            case element(tei:mod) return
                if ($node/@type eq "phase") then ()  (: TODO: alte Codierung Welscher Gast :)
                else if (contains($node/@ana,'hc:')) then
                    element span {
                        attribute class {teicommon:ana2class($node,'t-mod-')},
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                else teicommon:transform-to-html($node/node(), $func, $rendering)

            case element(tei:delSpan) return
                element span {
                    attribute class {'t-ms-hc_DeletionSpan'},
                    if ($node/@corresp) then attribute data-spanto {$node/@corresp} (: corresp wird verwendet, wenn anchor auch vor milestone sein kann :)
                    else if ($node/@spanTo) then attribute data-spanto {$node/@spanTo}
                    else ()
                }

            case element(tei:del) return
                element span {
                    if ($node/@xml:id) then (
                        attribute id { $node/@xml:id },
                        if (map:contains($rendering,'substJoin-map')) then
                            if (map:contains(map:get($rendering,'substJoin-map'),'mod2substJoin')) then
                                if (map:contains(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$node/@xml:id/string())) then
                                    attribute data-subst-id {map:get(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$node/@xml:id/string())}
                                else ()
                            else ()
                        else ()
                    )
                    else (),
                    attribute class { "t-del", teicommon:rendition2class($node)},
                    (: ToDo: @rend alte Codierung :)
                    if ($node/@rend and not($node/@rendition)) then attribute data-rend { string($node/@rend) } else (),
                    if ($node/@rendition) then attribute data-rend { string($node/@rendition) } else (), (: data-rend zusätzlich zu Klasse für Beschreibung :)
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:addSpan) return
                element span {
                    attribute class {'t-ms-hc_AdditionSpan'},
                    if ($node/@corresp) then attribute data-spanto {$node/@corresp} (: corresp wird verwendet, wenn anchor auch vor milestone sein kann :)
                    else if ($node/@spanTo) then attribute data-spanto {$node/@spanTo}
                    else ()
                }
                
            case element(tei:add) return
                element span {
                    if ($node/@xml:id) then (
                        attribute id { $node/@xml:id },
                        if (map:contains($rendering,'substJoin-map')) then
                            if (map:contains(map:get($rendering,'substJoin-map'),'mod2substJoin')) then
                                if (map:contains(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$node/@xml:id/string())) then
                                    attribute data-subst-id {map:get(map:get(map:get($rendering,'substJoin-map'),'mod2substJoin'),$node/@xml:id/string())}
                                else ()
                            else ()
                        else ()
                    )
                    else (),
                    attribute class { "t-add", teicommon:rendition2class($node)},

                
                    if ($node/@rendition) then attribute data-rend { string($node/@rendition) } else (),  (: data-rend zusätzlich zu Klasse für Beschreibung :)
                    if ($node/@hei:placeRef) then attribute data-place { string($node/@hei:placeRef) }
                    else if ($node/@place) then attribute data-place { string($node/@place) } (: ToDo: alte Codierung :)
                    else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:subst) return
                    element span {
                        attribute id { if ($node/@xml:id) then $node/@xml:id else generate-id($node)},
                        attribute class { "t-subst" },
                        if (map:get($rendering,'data-line')) then teicommon:data-line-attr($node) else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                    
            case element(tei:substJoin) return ()

            case element(tei:unclear)
                return element span { attribute class { "tei-unclear" }, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:w) return (
                element span {
                        teicommon:copy_id($node,$rendering),
                        attribute class {
                            "t-w",
                            if ($node/@lemmaRef) then "t-w-lemma" else (),
                            if ($node/@part eq 'I' or $node/@part eq 'M') then "t-w-part" else (),
                            teicommon:transposed_class($node,$rendering),
                            if (contains($node/@ana,'hc:EditorialAdditionSpan')) then 't-in-supplied' else '',
                            if (contains($node/@ana,'hc:EditorialDeletionSpan')) then 't-in-surplus' else '',
                            if (contains($node/@ana,'hc:AdditionSpan')) then 't-in-add' else '',
                            if (contains($node/@ana,'hc:DeletionSpan')) then 't-in-del' else ''
                        },
                        if ($node/@lemmaRef) then attribute data-lid { $node/@lemmaRef } else (),
                        if ($node/@hei:revisionRef) then attribute data-revision {substring($node/@hei:revisionRef,2)} else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                },
                
                (: Verarbeitung von transpose :)
                teicommon:process_transposed_element_html($node, $func, $rendering)
            )
            
            case element(tei:pc) return (
                element span {
                    (: ToDo: editorisch eingefügte Elemente am übergeordneten reg festmachen :)
                    attribute class { "tei-pc", if ($node/@type eq 'editorial' or $node/parent::tei:reg) then "tei-pc-edt" else () },
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            )
            
            (: ToDo: @type weg, wird @ana benötigt? :)
            (:case element(tei:c) return element span { attribute class { "t-char"}, if ($node/@type) then attribute data-type { string($node/@type) } else (), teicommon:transform-to-html($node/node(), $func, $rendering) }:)
            case element(tei:c) return
                element span {
                    if ($node/@xml:id) then attribute id { $node/@xml:id } else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            
            case element(tei:q) return element span { attribute class { 't-quoted', if ($node/@ana) then teicommon:ana2class($node,'t-quote-') else ''}, teicommon:transform-to-html($node/node(), $func, $rendering) }
            
            case element(tei:g) return element span {attribute data-ref { $node/@ref }, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:space) return 
                if ($node/@dim eq 'vertical' or $node/@unit eq "lines") then
                    element div {
                        attribute class { 't-space t-vspace', if ($node/tei:certainty) then 't-space-unsure' else '' },
                        if ($node/@extent) then attribute data-extent {string($node/@extent)} else attribute data-extent {"unknown"},
                        if ($node/@quantity) then attribute data-quantity { string($node/@quantity)} else (),
                        if ($node/@unit) then attribute data-unit { string($node/@unit)} else (),
                        if ($node/child::tei:desc) then attribute data-desc { replace(string($node/tei:desc),'"','&quot;') } else ()
                        (: Außer desc kann es keine Kindelemenete geben: teicommon:transform-to-html($node/node(), $func, $rendering) :)
                    }
                else
                    element span {
                        attribute class { 't-space t-hspace', if ($node/tei:certainty) then 't-space-unsure' else '' },
                        if ($node/@extent) then attribute data-extent { string($node/@extent)} else (),
                        if ($node/@quantity) then attribute data-quantity { string($node/@quantity)} else (),
                        if ($node/@unit) then attribute data-unit { string($node/@unit)} else (),
                        if ($node/child::tei:desc) then attribute data-desc { replace(string($node/tei:desc),'"','&quot;') } else ()
                        (: Außer desc kann es keine Kindelemenete geben: teicommon:transform-to-html($node/node(), $func, $rendering) :)
                    }

            case element(tei:p) return
                if ($node/ancestor::tei:note) then (element span {attribute class {'t-p-in-note'}, if ($node/@xml:id) then attribute id {$node/@xml:id} else (), teicommon:transform-to-html($node/node(),$func, $rendering)})
                else (
                    element p {
                        if ($node/@xml:id) then attribute id {$node/@xml:id} else (),
                        if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                        attribute class {
                            if ($node/@rendition) then teicommon:rendition2class($node) else (),
                            if ($node/@ana eq "hc:SeparatorCharacterChunk") then 't-p-separator' else ''
                        },
                        if ($node/@n) then attribute data-n {$node/@n} else (),
                        teicommon:transform-to-html($node/node(),$func, $rendering)
                        
                    }
                )
                
            case element(tei:epigraph)
                return (element div {attribute class {'t-div-Epigraph'}, teicommon:transform-to-html($node/node(),$func, $rendering)})

            case element(tei:quote) return (
                if (contains($node/@ana,'hc:BlockQuotation')) then element div {attribute class {'t-quote', if ($node/@ana) then teicommon:ana2class($node,'t-quote-') else ''}, teicommon:transform-to-html($node/node(),$func, $rendering)}
                else element span {attribute class {'t-quote', if ($node/@ana) then teicommon:ana2class($node,'t-quote-') else ''}, teicommon:transform-to-html($node/node(),$func, $rendering)}
            )
            
            case element(tei:mentioned) return (
                element span {attribute class {'t-mentioned'}, teicommon:transform-to-html($node/node(),$func, $rendering)}
            )

            (:  Editorische Eingriffe :)
            case element(tei:surplus) return
                (element span { attribute class { "t-surplus" }, teicommon:transform-to-html($node/node(),$func, $rendering) })

            case element(tei:supplied) return
                (element span { attribute class { "t-supplied" }, if ($node/@reason) then attribute data-reason { string($node/@reason) } else (), if ($node/@cert) then attribute data-cert { string($node/@cert) } else (), teicommon:transform-to-html($node/node(),$func, $rendering) })

            case element(tei:reg) return
                 element span {
                     attribute class {
                        if ($node/@ana eq 'hc:HyphenRegularization') then 't-reg-hyph'
                        else if ($node/@ana eq 'hc:PunctuationRegularization') then 't-reg-punc'
                        else if ($node/@ana eq 'hc:TokenDelimiterRegularization') then 't-reg-token'
                        else 't-reg'
                     },
                     teicommon:transform-to-html($node/node(), $func, $rendering)
                 }

            case element(tei:orig) return
                element span {
                    attribute class {
                        if ($node/parent::tei:choice/tei:reg/@ana eq 'hc:HyphenRegularization') then 't-orig-hyph'
                        else if ($node/parent::tei:choice/tei:reg/@ana eq 'hc:PunctuationRegularization') then 't-orig-punc'
                        else if ($node/parent::tei:choice/tei:reg/@ana eq 'hc:TokenDelimiterRegularization') then 't-orig-token'
                        else if ($node/parent::tei:choice/tei:supplied) then 't-orig-supplied'
                        else 't-orig'
                    },
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:sic) return
                element span { attribute class {if ($node/parent::tei:choice) then 't-sic' else 't-sic-solo'}, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:corr) return
                element span { attribute class {'t-corr'}, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:app) return
                if ($node/@type eq "editorial") then
                    element span {
                        (: class tei-app-edt wird aktuell nicht weiterverarbeitet :)
                        attribute class { "tei-app-edt" },
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                else element span { attribute class { "tei-app tei-choice" }, teicommon:transform-to-html($node/node(),$func, $rendering)}
                
            case element(tei:lem) return
                element span { attribute class { "t-lem" }, if ($node/@resp) then attribute data-resp { string($node/@resp) } else (), teicommon:transform-to-html($node/node(),$func, $rendering)}

            case element(tei:rdg) return
                (: TODO: rdg/@rend='missing' alte Codierung WGD :)
                element span { attribute class { "t-rdg", if ($node/@rend eq 'missing') then "t-rdg-missing" else () }, teicommon:transform-to-html($node/node(),$func, $rendering)}

            case element(tei:handShift) return
                element span {
                    attribute class { 't-handshift', if ($node/@cert eq 'low') then 't-handshift-low' else ''},
                    attribute lang {if ($node/@xml:lang) then string($node/@xml:lang) else 'en'},
                    attribute dir {'ltr'},
                    if ($node/@new) then string($node/ancestor::tei:TEI//tei:handNote[@xml:id eq substring($node/@new,2)]) else 'unknown',
                    teicommon:transform-to-html($node/node(),$func, $rendering)
                }

            case element(tei:metamark) return
                element span { 
                    attribute class { "t-metamark" }, 
                    if ($node/@target) then attribute data-target { string($node/@target) } else (), 
                    
                    if ($node/@hei:placeRef) then attribute data-place { string($node/@hei:placeRef) }
                    else if ($node/@place) then attribute data-place { string($node/@place) } (: ToDo: alte Codierung :)
                    else (), 
                    
                    (: ToDo: alte Codierung :)
                    if ($node/@function and not($node/@ana)) then attribute data-ana { string($node/@function) } else (), 
                    if ($node/@ana) then attribute data-ana { string($node/@ana) } else (),
                    (: falls target auf ein transpose verweist, data-trans-id setzen = ID, auf die verwiesen wird :)
                    if (contains($node/@ana,'hc:TranspositionMark') and $node/@target) then (
                        if ($node/ancestor::tei:TEI//*[@xml:id eq substring($node/@target,2)] and local-name($node/ancestor::tei:TEI//*[@xml:id eq substring($node/@target,2)]) eq "transpose") then
                            attribute data-trans-id {substring($node/@target,2)}
                        else ()
                    ) else (),
                    teicommon:transform-to-html($node/node(),$func, $rendering)
                }
                
            case element(hei:cue) return
                element span {
                    attribute class { "t-cue", if ($node/@ana) then teicommon:ana2class($node,'t-cue-') else ''},
                    teicommon:transform-to-html($node/node(),$func, $rendering)
                }

            case element(tei:list) return
                (
                    (: ToDo: https://gitlab.ub.uni-heidelberg.de/editions/heieditions/-/issues/92 :)
                    
                    if ($node/tei:head) then element div {attribute class {'t-list-head'}, teicommon:transform-to-html($node/tei:head/node(),$func, $rendering)} else (),
                    (: nur tei:item weiterverarbeiten, nicht head oder br :)
                    if (contains($node/@rendition,'hc:ItemMarkerDecimal') or contains($node/@rendition,'hc:ItemMarkerLowerRoman')) then
                        element ol {attribute class {'t-list', if ($node/tei:item/tei:label) then 't-list-labeled-items' else if ($node/@rendition) then teicommon:list_type($node/@rendition) else ''}, teicommon:transform-to-html($node/tei:item,$func, $rendering)}
                    else
                        element ul {attribute class {'t-list', if ($node/tei:item/tei:label) then 't-list-labeled-items' else if ($node/@rendition) then teicommon:list_type($node/@rendition) else ''}, teicommon:transform-to-html($node/tei:item,$func, $rendering)}
                )
                
            case element(tei:item) return
                element li {
                    if ($node/@xml:id) then attribute id {string($node/@xml:id)} else (),
                    if ($node/parent::tei:listBibl) then (
                        (: für Konstrukt listBibl/item/bibl* :)
                        element div {attribute class {'t-lit'}, element div {attribute class {'t-citation'}, teicommon:transform-to-html($node/node(), $func, $rendering)}}
                    )
                    else (
                        if ($node/tei:label) then (
                            element div {attribute class {'t-list-label'}, teicommon:transform-to-html($node/tei:label/node(),$func, $rendering)},
                            element div {attribute class {'t-list-cont'}, teicommon:transform-to-html($node/node(),$func, $rendering)}
                        )
                        (: wenn kein tei:label, ersatzweise @n, wenn vorhanden :)
                        else if ($node/@n) then (
                            element div {attribute class {'t-list-label'}, teicommon:transform-to-html($node/@n,$func, $rendering)},
                            element div {attribute class {'t-list-cont'}, teicommon:transform-to-html($node/node(),$func, $rendering)}
                        )
                        else teicommon:transform-to-html($node/node(),$func, $rendering)
                    )
                }

            case element(tei:figure) 
                return
                (: ToDo: ??? :)
                if ($func eq "verse") then
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                else element div {
                    if ($node/@xml:id) then attribute id {string($node/@xml:id)} else (),
                    attribute data-facs {string($node/@facs)},
                    if ($node/@hei:placeRef) then attribute data-place { string($node/@hei:placeRef) }
                    else if ($node/@place) then attribute data-place { string($node/@place) } (: ToDo: alte Codierung :)
                    else (),
                    attribute data-prev {string($node/@prev)},
                    attribute data-next {string($node/@next)},
                    attribute data-type {string($node/@type)},
                    
                    if ($node/tei:figDesc) then attribute data-title {$node/tei:figDesc/string()} else (),
                    
                    (: HorizontalLine :)
                    if ($node/@ana eq 'hc:HorizontalLine') then (
                        attribute class {"t-fig-wrap t-fig-hc_InlineFigure" },
                        element div {attribute class {"t-fig-hc_HorizontalLine" }}
                    )
                    (: VerticalLine :)
                    else if ($node/@ana eq 'hc:VerticalLine') then (
                        attribute class { "t-fig-wrap t-fig-hc_InlineFigure" },
                        element div {attribute class {"t-fig-hc_VerticalLine" }}
                    )
                    (: Mit graphic oder nur Platzhalter, keine Abbildung codiert :)
                    else (
                        attribute class {
                            't-fig-wrap',
                            if ($node/@ana) then teicommon:ana2class($node,'t-fig-') else 't-fig-hc_DetachedFigure',
                            (: Auslagern in heiVIEWER-Spalte für Medien möglich? :)
                            if (contains($node/@ana,'hc:InlineFigure') or contains($node/@rendition,'hc:Embedded')) then ''
                            else if (not($node/tei:graphic or $node/tei:media)) then '' (: reine Stellvertreter ohne Medium nie auslagerbar :)
                            else (
                                't-fig-move',
                                (: Falls ausgelagert, Platzhalter ? :)
                                if (contains($node/@ana,'hc:DetachedFigure')) then '' else 't-fig-move-ph'
                            )
                        }
                    ),

                    if (not($node/tei:graphic or $node/tei:media)) then element div {attribute class {'t-fig-only-placeholder'}, if ($node/tei:figDesc) then attribute title {$node/tei:figDesc/string()} else (), element span {attribute class {'t-fig-figdesc'}, $node/tei:figDesc/string()}}
                    else (
                        if ($node/tei:graphic) then teicommon:transform-to-html($node/tei:graphic, $func, $rendering) else (),
                        if ($node/tei:media) then teicommon:transform-to-html($node/tei:media, $func, $rendering) else ()
                    ),

                    if ($node/@n or $node/tei:head or $node/tei:label) then
                        element div {
                            attribute class {'t-fig-head'},
                            
                            if ($node/tei:label) then teicommon:transform-to-html($node/tei:label, $func, $rendering)
                            else if ($node/@n) then element span {attribute class {'t-fig-label', if (contains($node/@ana,'hc:EditorialContent')) then 't-fig-label-edt' else ''}, string($node/@n)}
                            else (),
                            
                            if ($node/tei:head) then (element span {attribute class {'t-fig-caption', if (contains($node/@ana,'hc:EditorialContent')) then 't-fig-caption-edt' else ''}, teicommon:transform-to-html($node/tei:head, $func, $rendering)}) else ()
                        }
                    else (),
                    
                    if ($node/tei:figDesc) then element div {attribute class {'t-fig-figdesc'}, $node/tei:figDesc/string()} else (),
                    if ($node/tei:note) then element div {attribute class {'t-fig-note', if (contains($node/@ana,'hc:EditorialContent')) then 't-fig-note-edt' else ''}, teicommon:transform-to-html($node/tei:note/node(), $func, $rendering)} else ()
                }

            (: tei:figDesc wird schon beim übergeordneten div (tei:figure) und in tei:graphic verarbeitet :)
            case element(tei:figDesc) return ()

            case element(tei:media) return (
                (: RTI :)
                if ($node/@mimetype eq 'model/prs.relight+zip' or $node/@mimetype eq 'model/prs.relight-deepzoom+zip') then (
                    element div {
                        attribute data-uri {$node/@url},
                        attribute class {'t-media-rti'},
                        attribute data-mimetype {$node/@mimetype},
                        if ($node/@width) then attribute data-width {string($node/@width)} else (),
                        if ($node/@height) then attribute data-height {string($node/@height)} else ()
                    },
                    (: Download-Link :)
                    if ($node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference']) then
                        element div {
                            element a {
                                attribute class {'t-fig-download'},
                                if (matches($node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url,'^https?:')) then
                                    attribute href {$node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url}
                                else
                                    attribute data-uri {$node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url},
                                attribute target {'_blank'}
                            }
                        }
                    else if ($node/following-sibling::tei:graphic[@ana='hc:HighResolutionDigitalImageReference']) then
                        element div {
                            element a {
                                attribute class {'t-fig-download'},
                                if (matches($node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url,'^https?:')) then
                                    attribute href {$node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url}
                                else
                                    attribute data-uri {$node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url},
                                attribute target {'_blank'}
                            }
                        }
                    else ()
                )
                (: audio + video :)
                else (
                    element div {
                        (: ToDo: audio + video :)
                        attribute id {$node/@id},
                        attribute class {'t-fig-wrap t-fig-hc_DetachedFigure t-fig-move'},
                        if (starts-with($node/mimetype,'video')) then (
                            element video {
                                
                                    
                                    
                            }
                        )
                        else if (starts-with($node/mimetype,'audio')) then (
                            element audio {
                                    
                                    
                                    
                            }
                        )
                        else ()
                    }
                )
            )

            case element(tei:graphic) return
                if ($node/@ana eq 'hc:HighResolutionDigitalImageReference') then ()
                else (
                    if ($node/parent::tei:figure) then (
                        element img {
                            if (matches($node/@url,'^https?:')) then attribute src {$node/@url} else attribute data-uri {$node/@url},
                            if ($node/parent::tei:figure/child::tei:figDesc) then attribute alt {$node/parent::tei:figure/child::tei:figDesc/text()} else (),
                            (: bislang werden Größenangaben an tei:figure nur für InlineFigure übernommen :)   
                            if ($node/parent::tei:figure[contains(@ana,'hc:InlineFigure')]) then (
                                if ($node/parent::tei:figure/@width) then attribute width {string($node/parent::tei:figure/@width)} else (),
                                if ($node/parent::tei:figure/@height) then attribute height {string($node/parent::tei:figure/@height)} else ()
                            ) else (
                                (:if ($node/@width) then attribute width {string($node/@width)} else (),
                                if ($node/@height) then attribute height {string($node/@height)} else ():)
                            )
                        },
                        (: Download-Link :)
                        if ($node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference']) then
                            element a {
                                attribute class {'t-fig-download'},
                                if (matches($node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url,'^https?:')) then
                                    attribute href {$node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url}
                                else
                                    attribute data-uri {$node/preceding-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url},
                                attribute target {'_blank'}
                            }
                        else if ($node/following-sibling::tei:graphic[@ana='hc:HighResolutionDigitalImageReference']) then
                            element a {
                                attribute class {'t-fig-download'},
                                if (matches($node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url,'^https?:')) then
                                    attribute href {$node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url}
                                else
                                    attribute data-uri {$node/following-sibling::tei:graphic[@ana eq 'hc:HighResolutionDigitalImageReference'][1]/@url},
                                attribute target {'_blank'}
                            }
                        else if (not($node/@ana eq 'hc:LowResolutionDigitalImageReference')) then
                            element a {
                                attribute class {'t-fig-download'},
                                if (matches($node/@url,'^https?:')) then
                                    attribute href {$node/@url}
                                else
                                    attribute data-uri {$node/@url},
                                attribute target {'_blank'}
                            }
                        else ()
                    )
                    else ()
                )

            case element(tei:fw) return
                element div {
                    attribute class {concat('tei-fw-', string($node/@type)), if ($node/@ana) then teicommon:ana2class($node,'tei-fw-') else ()},
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            (:  Fussnoten, Glossen :)
            case element(tei:note) return
                (: hc-Codierung :)
                if (starts-with($node/@ana,'hc:')) then
                    element span {
                        attribute class { "t-note-edt" },
                        attribute data-ana {normalize-space(replace(string($node/@ana),'hc:EditorialContent',''))},
                        if ($node/@xml:id) then attribute id {$node/@xml:id} else (), (: vorh. xml:id übernehmen, für PURL zu Fußnoten :)
                        if (map:get($rendering,'data-line')) then teicommon:data-line-attr($node) else (),
                        if ($node/@target) then (attribute data-target {string($node/@target)}) else (),
                        element span {attribute class { "t-note-content" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                }
                    
                (: Beginn alte Codierung, ToDo: entfernen :)
                else if ($node/@type eq "gloss") then
                    element span {
                        attribute data-target {if (contains($node/@target,' ') and (not($node/@subtype eq 'interrupted_target'))) then concat('#range(', replace(replace(string($node/@target),' ',','),'#',''), ')') else string($node/@target)}, (: für Umstieg auf neues Verfahren :)
                        attribute data-ana { 'hc:Gloss' }, (: für Umstieg auf neues Verfahren :)
                        attribute class { "t-note-edt" },
                        element span {attribute class { "t-note-content" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                }
                else if ($node/@type eq "editorial" 
                    or $node/@type eq "alternative"
                    or $node/@type eq "regularization"
                    or $node/@type eq "correction"
                    or $node/@type eq "running_commentary"
                    or $node/@type eq "comment"
                    or $node/@type eq "editorial_comment") then
                    element span {
                        attribute data-target {if (contains($node/@target,' ') and (not($node/@subtype eq 'interrupted_target'))) then concat('#range(', replace(replace(string($node/@target),' ',','),'#',''), ')') else string($node/@target)}, (: für Umstieg auf neues Verfahren :)
                        attribute class { "t-note-edt", if (exists($node/@subtype)) then (concat('notype_', $node/@subtype)) else () },
                        element span {attribute class { "t-note-content" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                    }
                (: Ende alte Codierung :)
                
                else element span {
                    attribute class { "t-note" },
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:opener) return
                element span {attribute class { "t-opener" }, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:closer) return
                element span {attribute class { "t-closer" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                
            case element(tei:salute) return
                element span {attribute class { "t-salute" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                
            case element(tei:signed) return
                element span {attribute class { "t-signed" }, teicommon:transform-to-html($node/node(), $func, $rendering)}
                
            case element(tei:dateline) return
                element span { attribute class { "tei-dateline" }, teicommon:transform-to-html($node/node(), $func, $rendering)}

            case element(tei:gap) return (
                (: gap[@unit eq line] in sourceDoc-Ansicht als eigene Zeile ausgeben :)
                if (($func eq "page" or $node/ancestor::hei:sourceDocFragment) and $node/@unit eq "line") then (
                    teicommon:output-line("tei-row", "", element span {teicommon:gap($node)})
                )
                else if ($func eq "synoptic" and (contains($node/@ana,'hc:PassiveSynopticGap') or contains($node/@ana,'hc:ActiveSynopticGap'))) then
                    element div {
                        (:if ($func eq "synoptic" and $node/preceding-sibling::tei:linkGrp[@target eq concat('#',$node/@xml:id)]) then attribute data-syn-handle {'y'} else (),:)
                        teicommon:gap($node)
                    }
                else
                    element span {teicommon:gap($node)}
            )

            case element(tei:damage)
                return (element span {attribute class { "tei-damage" }, teicommon:transform-to-html($node/node(),$func, $rendering) })

            case element(tei:emph) return
                (: rendition schlägt Default-Auszeichnungen über @ana :)
                if ($node/@rendition) then element span {attribute class {teicommon:rendition2class($node)}, teicommon:transform-to-html($node/node(),$func, $rendering)}
                else if ($node/@ana eq "hc:EditorialEmphasis") then element span {attribute class {teicommon:ana2class($node,'t-rend-')}, teicommon:transform-to-html($node/node(),$func, $rendering)}
                else if (contains($node/@ana,"hc:StrongEmphasis") and contains($node/@ana,"hc:LightEmphasis")) then element strong {element i {teicommon:transform-to-html($node/node(),$func, $rendering)}}
                else if ($node/@ana eq "hc:StrongEmphasis") then element strong {teicommon:transform-to-html($node/node(),$func, $rendering)}
                else if ($node/@ana eq "hc:LightEmphasis") then element i {teicommon:transform-to-html($node/node(),$func, $rendering)}
                else element em {teicommon:transform-to-html($node/node(),$func, $rendering)}

            case element(tei:seg) return (
                element span { 
                    attribute class {
                        teicommon:transposed_class($node,$rendering),
                        if (contains($node/@ana,'hc:RunOverBelow')) then 't-line-below'
                        else if (contains($node/@ana,'hc:RunOverAbove')) then 't-line-above'
                        (: nur für hc:LineSegment, die keine Überläufe sind: :)
                        else if (contains($node/@ana,'hc:LineSegment')) then 't-line-seg'
                        else if (contains($node/@ana,'hc:AlternativeSourceReading')) then if ($node/preceding-sibling::tei:seg) then 't-rdg' else 't-lem'
                        else if (contains($node/@ana,'hc:AbbreviatedTokenSegment')) then ('t-abbr', if (not($node/parent::tei:choice)) then 't-abbr-solo' else '')
                        else if (contains($node/@ana,'hc:ExpandedTokenSegment')) then ('t-expan', if ($node/parent::tei:choice and $node/preceding-sibling::*[1][local-name() eq 'expan']) then 't-expan-2' else '')
                        else if (contains($node/@ana,'hc:EditorialEmphasis')) then teicommon:ana2class($node,'t-rend-')
                        else if (contains($node/@ana,'hc:EditorialAdditionSpan')) then 't-in-supplied'
                        else if (contains($node/@ana,'hc:EditorialDeletionSpan')) then 't-in-surplus'
                        else if (contains($node/@ana,'hc:AdditionSpan')) then 't-in-add'
                        else if (contains($node/@ana,'hc:DeletionSpan')) then 't-in-del'
                        else (),
                        if ($node/@ana) then (teicommon:ana2class($node,'t-seg-')) else (),
                        if ($node/@rendition) then teicommon:rendition2class($node) else '',
                        teicommon:copy_id($node,$rendering)
                    },
                    if ($node/@hei:revisionRef) then attribute data-revision {substring($node/@hei:revisionRef,2)} else (),
                    teicommon:transform-to-html($node/node(),$func, $rendering)
                },
                
                (: Verarbeitung von transpose :)
                teicommon:process_transposed_element_html($node, $func, $rendering)
            )

            case element(tei:rhyme)
                return element span { attribute class { "t-rhyme", if ($node/@type) then concat('t-rhyme-',string($node/@type)) else ()}, teicommon:transform-to-html($node/node(),$func, $rendering) }

            case element(tei:linkGrp)
                return () (: zunächst komplett unterdrücken. Ggf. Verwendung bei Synopse (erzeugen von "Handles" für Wechsel Focuszeile?) :)

            case element(tei:ptr)
                return element span { attribute class { "tei-ptr" }, attribute data-type { $node/@type }, if ($node/@target) then attribute data-target { $node/@target } else (), if ($node/@corresp) then attribute data-corresp { $node/@corresp } else (),teicommon:transform-to-html($node/node(),$func, $rendering)}

            case element(tei:persName) return
                element span {
                    attribute class {'t-pers'},
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:orgName) return
                element span {
                    attribute class {'t-org'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:placeName) return
                element span {
                    attribute class {'t-place'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    if ($node/@cert) then attribute data-cert {string($node/@cert)}
                    else if ($node/parent::tei:origPlace/@cert) then attribute data-cert {string($node/parent::tei:origPlace/@cert)}
                    else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:name) return
                element span {
                    attribute class {if (contains($node/@ana,'hc:EventName') or contains($node/@ana,'hc:EventReference')) then 't-event' else 't-rs'},
                    if ($node/@ana) then attribute data-ana {string($node/@ana)} else (),
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:eventName) return
                element span {
                    attribute class {'t-event'},
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            
            case element(tei:origDate) return
                element span {
                    attribute class {'t-origdate'},
                    if ($node/@cert) then attribute data-cert {string($node/@cert)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            case element(tei:rs) return
                element span {
                    attribute class {'t-rs'},
                    if ($node/@ana) then attribute data-ana {string($node/@ana)} else (),
                    if ($node/@ref) then attribute data-ref {string($node/@ref)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
            
            case element(tei:num) return
                element span {
                    attribute class {'tei-num'},
                    if ($node/@value) then attribute data-value {string($node/@value)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }
                
            (: transpose selbst wird nicht mehr ausgegeben. Alle Informationen stecken in .t-trans-aut und .t-trans-aut-orig
            case element(tei:transpose)
                return element span { attribute class { "tei-transpose" }, teicommon:transform-to-html($node/node(), $func, $rendering)}:)
                
            (: link wird nicht ausgegeben. Alle Informationen stecken in .t-trans-edt und .t-trans-edt-orig
            case element(tei:link)
                return ():)

            case element(tei:table)
                return element div {
                    if ($node/@xml:id) then attribute id {string($node/@xml:id)} else (),
                    attribute class { 
                        "t-table-wrap",
                        if ($node/@ana) then teicommon:ana2class($node,'t-table-') else 't-table-hc_DetachedTable',
                        if (contains($node/@rendition,'hc:NoBorder')) then 't-table-hc_NoBorder' else '',

                        (: Auslagern in heiVIEWER-Spalte für Medien möglich? :)
                        if (contains($node/@rendition,'hc:Embedded'))
                                then ''
                                else (
                                    't-tab-move',
                                    (: Falls ausgelagert, Platzhalter ? :)
                                    if (contains($node/@ana,'hc:DetachedTable')) then '' else 't-tab-move-ph'
                                )
                    },
                    element table {
                        if ($node/@style) then attribute style {string($node/@style)} else (),
                        teicommon:transform-to-html($node/node(), $func, $rendering)
                    }
                }

            case element(tei:row)
                return element tr {
                    if ($node/@xml:id) then attribute id {string($node/@xml:id)} else (),
                    if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (), 
                    if ($node/@n) then element th {attribute class {"t-tablno", if (matches($node/@n,'[05]$')) then 'mod5' else if (not(fn:number($node/@n))) then 'mod5' else ''}, element span {string($node/@n)}} else (),
                    if ($node/@style) then attribute style {string($node/@style)} else (),
                    teicommon:transform-to-html($node/node(), $func, $rendering)
                }

            case element(tei:cell)
                return
                    element {if ($node/@role eq "label" or $node/ancestor::tei:row[1]/@role eq "label") then 'th' else 'td'} {
                        if ($node/@rendition or $node/@style or $node/@hei:width) then (
                            attribute style {
                                if ($node/@style) then concat(string($node/@style),' ') else '',
                                (:if ($node/@hei:width) then concat('width:',if ($node/parent::tei:row/@n) then 'calc(' else '',string($node/@hei:width),if ($node/parent::tei:row/@n) then ' - 30px);' else '; ') else '',:)
                                if ($node/@hei:width) then concat('width:',string($node/@hei:width),'; ') else '',
                                if ($node/@rendition eq 'hc:FlushLeft') then 'text-align: left;'
                                else if ($node/@rendition eq 'hc:FlushRight') then 'text-align: right;'
                                else if ($node/@rendition eq 'hc:Centered') then 'text-align: center;'
                                else if ($node/@rendition eq 'hc:Justified') then 'text-align: justify;'
                                else ()
                            }
                        ) else(),
                        if ($node/@cols) then attribute colspan {string($node/@cols)} else (),
                        if ($node/@rows) then attribute rowspan {string($node/@rows)} else (),
                        element span {teicommon:transform-to-html($node/node(),$func, $rendering)}
                    }

            case element(mathml:math) return element math { namespace mathml {'http://www.w3.org/1998/Math/MathML'}, $node/node()}

            default
                return teicommon:transform-to-html($node/node(), $func, $rendering)
};

declare function teicommon:transform-to-txt($nodes as node()*, $rendering)
(: rendering:
 :   - text-mode: diplomatic (default), editor
 :        
 :   - text-ed_norm: diplomantic, editor (für reg/orig, übersteuert text-mode)
 :   - text-ed_interventions: diplomatic, editor (für corr/sic, übersteuert text-mode)
 :   - text-abbr: abbr (default), expan (übersteuert text-mode)
 :   - text-filter-note: yes, no, yes-id (note mit @xml:id werden nicht ausgegeben)
 :   - text-lb: linefeed, no, beliebiger Trennstring
 :  :)

as item ()*
{
    for $node in $nodes
    return
        (: alle Tags innerhalb hc:EditorialAdditionSpan unterdrücken, wenn per Option diplomatische Fassung angezeigt werden soll :)
        if (contains($node/@ana,'hc:EditorialAdditionSpan') and not(map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor'))) then ''
        
        (: alle Tags innerhalb hc:EditorialDeletionSpan unterdrücken, wenn per Option Editor-Fassung angezeigt werden soll :)
        else if (contains($node/@ana,'hc:EditorialDeletionSpan') and (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor'))) then ''
        
        else typeswitch ($node)
            case comment() return ''
            
            case text() return
                if ($node/parent::tei:zone or $node/parent::tei:surface) then '' (: Quellenansicht: Keine direkten Textknoten unter surface oder zone ausgeben :)
                else if (not(normalize-space($node))) then
                    (: in Textausgabe zu Quellenansicht: Keine Whitespaces zwischen Zeilen nach w/@part eq 'I' oder w/@part eq 'M':)
                    if ($node/preceding-sibling::*[1][local-name() eq 'line'] and $node/preceding-sibling::*[1][local-name() eq 'line']//tei:w[@part eq 'I' or @part eq 'M']) then '' else ' '
                else $node (: Blank am Anfang und Ende von Textknoten muss erhalten bleiben! Kein normalize-space! :)
                
            case element(tei:lb) return
                if (map:get($rendering,'text-lb') eq "linefeed") then
                    if ($node/@break eq 'no') then 
                        if ($node/preceding-sibling::*[1]/descendant-or-self::tei:w[@part]) then codepoints-to-string(10)
                        else ('-',codepoints-to-string(10))
                    else codepoints-to-string(10)
                else if (map:get($rendering,'text-lb')) then
                    if ($node/@break eq 'no') then 
                        if ($node/preceding-sibling::*[1]/descendant-or-self::tei:w[@part]) then map:get($rendering,'text-lb')
                        else ('-',map:get($rendering,'text-lb'))
                    else map:get($rendering,'text-lb')
                else
                    if ($node/@break eq 'no') then ''
                    else ' '
            
            case element(tei:line) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    (teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string()))),codepoints-to-string(10))
                else
                    (teicommon:transform-to-txt($node/node(), $rendering),codepoints-to-string(10))
                
            case element(tei:cb) return ''
            
            case element(tei:pb) return ''
            
            case element(tei:div) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    (codepoints-to-string(10), teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string()))), codepoints-to-string(10))
                else
                    (codepoints-to-string(10), teicommon:transform-to-txt($node/node(), $rendering), codepoints-to-string(10))
            
            case element(tei:l) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string())))
                else
                    teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:lg) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string())))
                else
                    teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:w) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string())))
                else
                    (: Trennstrich erzeugen, wenn nicht codiert :)
                    if (
                        ($node/@part eq 'I' or $node/@part eq 'M')
                        and $node/ancestor::tei:line
                        and not($node/following-sibling::*[1]/local-name() eq 'metamark')
                        and not($node/following-sibling::*[1]//tei:metamark)
                    ) then (teicommon:transform-to-txt($node/node(), $rendering),'-')
                    else
                        teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:seg) return
                (: Umstellung Herausgeber? :)
                if (teicommon:show_edt_transposed_txt($node,$rendering) or teicommon:show_aut_transposed_txt($node,$rendering)) then
                    teicommon:transform-to-txt(teicommon:transposed_element($node,$rendering),map:put($rendering,'transpose-id',teicommon:get_transpose_id($rendering,$node/@xml:id/string())))
                else
                    teicommon:transform-to-txt($node/node(), $rendering)
                    
            case element(tei:metamark) return teicommon:transform-to-txt($node/node(), $rendering) (: TODO: ggf. Trennstriche vereinheitlichen? :)
            
            case element(tei:corr) return
                if (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor')) then teicommon:transform-to-txt($node/node(), $rendering)
                else ()
                
            case element(tei:supplied) return
                if (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor')) then teicommon:transform-to-txt($node/node(), $rendering)
                else ()
            
            case element(tei:sic) return
                if (not($node/parent::tei:choice)) then teicommon:transform-to-txt($node/node(), $rendering) (: alleinstehendes sic :)
                else
                    if (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor')) then ()
                    else teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:surplus) return
                if (map:get($rendering,'text-ed_interventions') eq 'editor' or (not(map:get($rendering,'text-ed_interventions')) and map:get($rendering,'text-mode') eq 'editor')) then ()
                else teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:reg) return
                if (map:get($rendering,'text-ed_norm') eq 'editor' or (not(map:get($rendering,'text-ed_norm')) and map:get($rendering,'text-mode') eq 'editor')) then teicommon:transform-to-txt($node/node(), $rendering)
                else ()
            
            case element(tei:orig) return
                if (map:get($rendering,'text-ed_norm') eq 'editor' or (not(map:get($rendering,'text-ed_norm')) and map:get($rendering,'text-mode') eq 'editor')) then ()
                else teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:abbr) return
                if (map:get($rendering,'text-abbr') eq 'editor' or (not(map:get($rendering,'text-abbr')) and map:get($rendering,'text-mode') eq 'editor')) then ()
                else teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:expan) return
                if (map:get($rendering,'text-abbr') eq 'editor' or (not(map:get($rendering,'text-abbr')) and map:get($rendering,'text-mode') eq 'editor')) then teicommon:transform-to-txt($node/node(), $rendering)
                else ()
                
            case element(tei:am) return
                if (map:get($rendering,'text-abbr') eq 'editor' or (not(map:get($rendering,'text-abbr')) and map:get($rendering,'text-mode') eq 'editor')) then ()
                else teicommon:transform-to-txt($node/node(), $rendering)
            
            case element(tei:ex) return
                if ($node/preceding-sibling::*[1][local-name() eq 'ex']) then '' (: grundsätzlich beim Textexport nur erste Auflösungsvariante berücksichtigen :)
                else if (map:get($rendering,'text-abbr') eq 'editor' or (not(map:get($rendering,'text-abbr')) and map:get($rendering,'text-mode') eq 'editor')) then teicommon:transform-to-txt($node/node(), $rendering)
                else ()
            
            case element(tei:note) return
                if ($node/@xml:id) then
                    if (map:get($rendering,'text-filter-note') eq 'yes' or map:get($rendering,'text-filter-note') eq 'yes-id') then ''
                    else
                        if (map:get($rendering,'text-mode') eq 'editor') then (' [', teicommon:transform-to-txt($node/node(), $rendering),'] ')
                        else ''
                else
                    if (map:get($rendering,'text-filter-note') eq 'yes') then ''
                    else 
                        if (map:get($rendering,'text-mode') eq 'editor') then (' [', teicommon:transform-to-txt($node/node(), $rendering),'] ')
                        else ''
                        
            case element(hei:cue) return () (: erst mal nicht ausgeben :)
            
            case element(tei:space) return
                if ($node/@extent eq '0') then '' else ' '
            
            (: Default: case element(tei:label) return teicommon:transform-to-txt($node/node(), $rendering) :)
            
            case element(tei:head) return (
                    if (contains($node/@ana,'hc:EditorialContent')) then codepoints-to-string(10) else '',
                    teicommon:transform-to-txt($node/node(), $rendering),
                    if (contains($node/@ana,'hc:EditorialContent')) then codepoints-to-string(10) else ''
                )
            
            (: Default: case element(tei:add) return teicommon:transform-to-txt($node/node(), $rendering)  - wird ohne Kennzeichnung ausgegeben :)
            
            case element(tei:del) return 
                if (map:get($rendering,'text-mode') eq 'editor') then ''
                else ('〚',teicommon:transform-to-txt($node/node(), $rendering),'〛') (: Ausgabe mit Marker :)
            
            (: Default: case element(tei:subst) return teicommon:transform-to-txt($node/node(), $rendering)  - keine besondere Verarbeitung :)
            
            (: Default: case element(tei:substJoin) return teicommon:transform-to-txt($node/node(), $rendering)  - keine besondere Verarbeitung :)
            
            case element(tei:milestone) return
                if (contains($node/@ana,'hc:DeletionSpan')) then '〚'
                else ''
            
            case element(tei:anchor) return
                if ($node/@xml:id) then
                    if ($node/ancestor::tei:TEI//tei:milestone[@spanTo eq substring($node/@xml:id,2)][contains(@ana,'hc:DeletionSpan')]) then '〛'
                    else ''
                else ''    
            
            case element(tei:num) return (
                if ($node/@value) then ('[',$node/@value/string(),']') else '',
                teicommon:transform-to-txt($node/node(), $rendering)
            )
            
            default
                return teicommon:transform-to-txt($node/node(), $rendering)
};                     

(:  :declare function teicommon:transform-to-text($nodes as node()*, $func, $rendering):)
(:  option-editorial: :)
(:       '' (default): editorische Eingriffe unterdrücken :)
(:      'ed_footnote_note': Nur Fussnoten ausgeben :)
(:      'all': Editorische Eingriffe direkt im Text anzeigen :)

(:  :as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case text() return
                if (map:get($rendering,'option-editorial') != 'ed_footnote_note') then (
                    if (not(normalize-space($node))) then:)
                        (: in Textausgabe zu Quellenansicht: Keine Whitespaces nach w/@part eq 'I' oder w/@part eq 'M':)
                        (:if ($node/preceding-sibling::*[1][local-name() eq 'line'] and $node/preceding-sibling::*[1][local-name() eq 'line']//tei:w[@part eq 'I' or @part eq 'M']) then '' else ' '
                    else normalize-space($node)
                )
                else ()
                    
                
            case element(tei:head)
                return (codepoints-to-string(10),codepoints-to-string(10),teicommon:transform-to-text($node/node(),$func, $rendering),codepoints-to-string(10),codepoints-to-string(10))
            
            case element(tei:line) 
                return (
                    teicommon:transform-to-text($node/node(),$func, $rendering),
                    if ($node//tei:w[@part eq 'I' or @part eq 'M']) then () else text { "&#10;" }
                )
            
            case element(tei:w) return
                teicommon:transform-to-text($node/node(),$func, $rendering)
            case element(tei:pc)
                return ( $node/text(), if ($node/following-sibling::*[1]) then if ($node/following-sibling::*[1]/name() ne 'space') then text { ' ' } else () else text { ' ' }):)
            (: Space :)
            (:case element(tei:space)
                return if ($node/@extent eq '0') then () else text {' '}:)
                
            (: Abkürzungen :)
            (:case element(tei:abbr)
                return
                    if (map:get($rendering,'option-editorial') = 'ed_footnote_note' or map:get($rendering,'option-editorial') = 'expan') then ()
                    else teicommon:transform-to-text($node/node(),'', $rendering)
                    
            case element(tei:expan)
                return
                    if (map:get($rendering,'option-editorial') = 'all') then (text { ' [' }, teicommon:transform-to-text($node/node(),'', $rendering), text { '] ' })
                    else
                        if (map:get($rendering,'option-editorial') = 'ed_footnote_note') then (
                            codepoints-to-string(10),
                            teicommon:transform-to-text($node/node(),'', map:merge(($rendering,map{'option-editorial': 'all'}),map{"duplicates":"use-last"}))
                        )
                        else if (map:get($rendering,'option-editorial') = 'expan') then (teicommon:transform-to-text($node/node(),'', $rendering))
                        else ()
            :)
            (: codepoint-to :)
            (:case element(tei:corr)
                return 
                    if (map:get($rendering,'option-editorial') = 'all') then (text { ' {{{' }, teicommon:transform-to-text($node/node(),'', $rendering), text { '}}} ' })
                    else
                        if (map:get($rendering,'option-editorial') = 'ed_footnote_note') then (codepoints-to-string(10), teicommon:transform-to-text($node/node(),'', map:merge(($rendering,map{'option-editorial': 'all'}),map{"duplicates":"use-last"})))
                        else ():)
            (: sic :)
            (: reg :)
            (:case element(tei:reg)
                return
                    if (map:get($rendering,'option-editorial') = 'all') then (text { ' {{{' }, teicommon:transform-to-text($node/node(),'', $rendering), text { '}}} ' })
                    else
                        if (map:get($rendering,'option-editorial') = 'ed_footnote_note') then (codepoints-to-string(10), teicommon:transform-to-text($node/node(),'', $rendering))
                        else ()
            :)            
            (: supplied :)
            (:case element(tei:supplied) wenn innerhalb Wort???
                return (text { ' {{{' }, teicommon:transform-to-text($node/node(),'', $rendering), text { '}}} ' })            :)
            
            (: mod 
               @type="phase" wird nicht ausgegeben :)
            (:case element(tei:mod) 
                return if ($node/@type eq "phase") then () else teicommon:transform-to-text($node/node(),'', $rendering):)
            (:case element(tei:del)
                return text { '' }:)
                
            (: Note :)
            (:case element(tei:note)
                return
                    if (map:get($rendering,'option-editorial') = 'all') then (text { ' {{{' }, teicommon:transform-to-text($node/node(),'', $rendering), text { '}}} ' })
                    else
                        if (map:get($rendering,'option-editorial') = 'ed_footnote_note') then (codepoints-to-string(10), teicommon:transform-to-text($node/node(),'',map:merge(($rendering,map{'option-editorial': 'all'}),map{"duplicates":"use-last"})))
                        else ()
            :)
            (: Referenzen, ToDo: Auflösgen und Text ergänzen :)
            (:case element(tei:persName)
                return teicommon:transform-to-text($node/node(),'', $rendering)
            
            case element(tei:orgName)
                return teicommon:transform-to-text($node/node(),'', $rendering)
                
            case element(tei:placeName)
                return teicommon:transform-to-text($node/node(),'', $rendering)
                
            case element(tei:rs)
                return teicommon:transform-to-text($node/node(),'', $rendering)
            :)
            
            (: Kommentare und Label nicht ausgeben :)
            (:case comment()
                return text { '' }
                
            case element(tei:label)
                return text { '' }
            default
                return teicommon:transform-to-text($node/node(),'', $rendering)
};:)

declare function teicommon:transform-to-xml($nodes as node()*)
as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case text()
                return $node
            (: Kommentare nicht ausgeben :)
            case comment()
                return text { '' }
            default
                return teicommon:transform-to-xml($node/node())
};

(: ToC :)

(:  Verarbeitung von head-Tags bei der Generierung einer ToC :)
declare function teicommon:head-transform-to-html($nodes as node()*, $func, $rendering, $begin)
as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case text()
                return $node
            case element(tei:choice) return (
                (: Bei choice werden im ToC nur bestimmte Subtags ausgegeben.
                ToDo: Die Liste muss ggf. noch erweitert werden :)
                teicommon:head-transform-to-html($node/tei:expan,$func,$rendering,$begin),
                teicommon:head-transform-to-html($node/tei:ex[not(ancestor::tei:expan)],$func,$rendering,$begin),
                teicommon:head-transform-to-html($node/tei:seg[@ana eq 'hc:ExpandedTokenSegment'][1],$func,$rendering,$begin),
                teicommon:head-transform-to-html($node/tei:reg,$func,$rendering,$begin),
                teicommon:head-transform-to-html($node/tei:sic,$func,$rendering,$begin)
            )
            case element(tei:note) return ''
            case element(tei:lb) return
                if ($node/@break eq 'no') then '' else ' '
            default
                return teicommon:head-transform-to-html($node/node(),$func,$rendering,$begin)
};

(: Generierung einer ToC aus der TEI-Datei 
   Alle Tags mit Ausnahme bestimmter div-Tags werden ignoriert :)
declare function teicommon:sections-transform-to-html($nodes as node()*, $func, $rendering, $begin)
as item ()*
{
    for $node in $nodes
    return
        typeswitch ($node)
            case element(tei:div) return
                if (not(contains($node/@rendition,'hc:SuppressInTOC') or contains($node/@ana,'hc:EmbeddedEdition'))) then
                    element li {
                        if ($node/@xml:id) then attribute data-target {$node/@xml:id} else (),
                        if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else (),
                        attribute class {'t-toc-pubpart', if (contains($node/@rendition,'hc:DisplayDivision')) then 't-toc-display-div' else '', teicommon:ana2class($node,'t-toc-div-'), if ($begin and not($node/ancestor-or-self::*[@xml:id eq $begin]) and not($node/descendant::*[@xml:id eq $begin])) then 't-toc-inactive' else (if ($node/@xml:id eq $begin) then 't-toc-active' else ())},
                        if ($node/@ana eq 'hc:Section') then attribute data-sec-level {count($node/ancestor::tei:div[@ana eq 'hc:Section'])+1} else (),
                        element span {
                            if ($node/@n) then element span {attribute class {'t-label'}, string($node/@n)} else (),
                            element span {
                                attribute class {'t-toc', if ($node/tei:head) then () else 't-toc-notit'},
                                if ($node/tei:head) then teicommon:head-transform-to-html($node/tei:head[1],$func,$rendering,$begin) else ()
                            }
                        },
                        if ($node/tei:div[not(contains(@rendition,'hc:SuppressInTOC') or contains(@ana,'hc:EmbeddedEdition'))]) then (
                            element ul {teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin)}
                        ) else ()
                    }
                else (teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin))
            case element(tei:front) return
                if (not(contains($node/@rendition,'hc:SuppressInTOC') or contains($node/@ana,'hc:EmbeddedEdition'))) then
                    element li {
                        if ($node/@xml:id) then attribute data-target {$node/@xml:id} else (),
                        if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else (),
                        attribute class {'t-toc-pubpart', if (contains($node/@rendition,'hc:DisplayDivision')) then 't-toc-display-div' else '', 't-toc-div-Front', if ($begin and not($node/ancestor-or-self::*[@xml:id eq $begin]) and not($node/descendant::*[@xml:id eq $begin])) then 't-toc-inactive' else (if ($node/@xml:id eq $begin) then 't-toc-active' else ())},
                        element span {
                            element span {
                                attribute class {'t-toc', if ($node/tei:head) then () else 't-toc-notit'},
                                if ($node/tei:head) then teicommon:head-transform-to-html($node/tei:head[1],$func,$rendering,$begin) else ()
                            }
                        },
                        if ($node/tei:div[not(contains(@rendition,'hc:SuppressInTOC'))]) then (
                            element ul {teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin)}
                        ) else ()
                    }
                else (teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin))
            case element(tei:back) return
                if (not(contains($node/@rendition,'hc:SuppressInTOC') or contains($node/@ana,'hc:EmbeddedEdition'))) then
                    element li {
                        if ($node/@xml:id) then attribute data-target {$node/@xml:id} else (),
                        if ($node/@xml:lang) then attribute lang {$node/@xml:lang} else (),
                        (: TODO: Weitere Sprachen? :)
                        if ($node/@xml:lang and index-of(('ar','he'),$node/@xml:lang)) then attribute dir {"rtl"} else (),
                        attribute class {'t-toc-pubpart', if (contains($node/@rendition,'hc:DisplayDivision')) then 't-toc-display-div' else '', 't-toc-div-Back', if ($begin and not($node/ancestor-or-self::*[@xml:id eq $begin]) and not($node/descendant::*[@xml:id eq $begin])) then    't-toc-inactive' else (if ($node/@xml:id eq $begin) then 't-toc-active' else ())},
                        element span {
                            element span {
                                attribute class {'t-toc', if ($node/tei:head) then () else 't-toc-notit'},
                                if ($node/tei:head) then teicommon:head-transform-to-html($node/tei:head[1],$func,$rendering,$begin) else ()
                            }
                        },
                        if ($node/tei:div[not(contains(@rendition,'hc:SuppressInTOC'))]) then (
                            element ul {teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin)}
                        ) else ()
                    }
                else (teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin))
            default
                return teicommon:sections-transform-to-html($node/node(),$func,$rendering,$begin)
};



