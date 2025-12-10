xquery version "3.1";

import module namespace teicommon = "http://exist-db.org/xquery/teicommon" at "teicommon.xq";
declare namespace tei = "http://www.tei-c.org/ns/1.0";
declare namespace hei = "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS";
declare namespace mathml = "http://www.w3.org/1998/Math/MathML";
declare namespace functx = "http://www.functx.com";
 

let $rendering := map{
    'data-line': true(),
    'text-mode': 'diplomatic', 
    'text-lb': 'linefeed', 
    'context': 'semantic'
}
for $node in doc("file:/home/gustavo/Dokumente/Editionen/EditionArmerHeinrich/texts/AH_A.xml")
return teicommon:transform-to-html($node, 'page', $rendering)

