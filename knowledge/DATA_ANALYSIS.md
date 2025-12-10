# TEI Data Analysis for heipy Test Suite

## Overview
This document analyzes the TEI XML structure used in the **heiEDITIONS** project for digital scholarly editions of medieval manuscripts, based on documentation from "Hartmann von Aue – digital" and example files from various editions.

## Data Sources Analyzed
1. **handbuch.txt** - Comprehensive TEI handbook for Hartmann von Aue digital editions (1045 lines)
2. **Gregoire_b_London.xml** - Fragment of "La Vie de saint Grégoire" (British Library ms. Additional 47663)
3. **Max_und_Moritz_A.xml** - Test document with basic structure
4. **Max_und_Moritz_B.xml** - Test document with variant structure and additional features

---

## 1. Document Structure

### 1.1 XML Declaration and Schema
All documents follow this pattern:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng"
    type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng"
    type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>

<!DOCTYPE TEI SYSTEM "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/declarations/heieditions-entities.txt">

<TEI xmlns="http://www.tei-c.org/ns/1.0"
     xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS">
```

**Key Features**:
- Dual validation: RelaxNG structure + Schematron rules
- Entity declarations for special characters (MUFI)
- Custom `hei:` namespace for heiEDITIONS extensions
- Ontology-based `ana` attributes using `hc:` prefix

### 1.2 Root Structure
```
TEI
├── teiHeader (metadata)
│   ├── fileDesc (publication info)
│   ├── encodingDesc (encoding rules)
│   └── (optional) revisionDesc
├── facsimile (page/zone mapping)
└── text (actual content)
    ├── (optional) front (titles, prologues)
    ├── body (main text)
    └── (optional) back (colophons, appendices)
```

---

## 2. Header Structure (teiHeader)

### 2.1 fileDesc - Publication Metadata
Complete metadata including:
- **Title** with `ana="hc:MainTitle"` and `ana="hc:Subtitle"`
- **Author** with GND identifiers
- **Editor** with GND and ORCID identifiers
- **Manuscript identifier** (settlement, repository, shelfmark, siglum)
- **Digital facsimile** references (with IIIF manifest URLs)
- **DOI** for edition and reading view
- **Bibliographic reference** (`ana="hc:RecommendedBibliographicReference"`)

Example from Gregoire:
```xml
<msIdentifier>
    <settlement>
        <placeName>London</placeName>
        <idno ana="hc:GNDURI">http://d-nb.info/gnd/4074335-4</idno>
    </settlement>
    <repository>
        <orgName>British Library</orgName>
        <idno ana="hc:GNDURI">https://d-nb.info/gnd/1023420-2</idno>
    </repository>
    <idno ana="hc:Shelfmark">ms. Additional 47663</idno>
    <idno ana="hc:EditorialSiglum">b</idno>
</msIdentifier>
```

### 2.2 encodingDesc - Encoding Rules
```xml
<encodingDesc>
    <listPrefixDef>
        <prefixDef ident="hc" matchPattern="(.+)"
            replacementPattern="https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/$1"/>
        <prefixDef ident="char" matchPattern="(.+)"
            replacementPattern="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/declarations/chars.xml#$1"/>
    </listPrefixDef>
    <hei:elementsWithTokenizedContent include="l head ab trailer"/>
</encodingDesc>
```

**Key Concept**: `hei:elementsWithTokenizedContent` declares which elements contain word-level tokenization.

---

## 3. Facsimile Structure

### 3.1 Page-Image Synchronization
The `<facsimile>` element provides detailed page-zone mapping:

```xml
<surface ana="hc:Page" xml:id="b_84r" n="84r">
    <graphic url="https://digi.ub.uni-heidelberg.de/diglit/bl_add47663/0001" mimeType="image/*"/>
    <zone ana="hc:HorizontalLayout">
        <zone ana="hc:MainColumn hc:TextZone" xml:id="b_84r-a" n="a"/>
        <zone ana="hc:MainColumn hc:TextZone" xml:id="b_84r-b" n="b"/>
    </zone>
</surface>
```

**Zone Types**:
- `hc:MainColumn` / `hc:Column` - Main text columns
- `hc:MarginalZone` - Marginal annotations
- `hc:HorizontalLayout` - Container for side-by-side zones
- `hc:TextZone` - Contains text content

**Zone Placement** (via `hei:placeRef`):
- `hc:PageTop`, `hc:PageBottom`
- `hc:PageMarginLeft`, `hc:PageMarginRight`
- `hc:ColumnMarginLeft`, `hc:ColumnMarginRight`

---

## 4. Text Structure Elements

### 4.1 Page, Column, Line Markers
**Structural Elements** (always empty):
- `<pb n="84r" facs="#b_84r"/>` - Page beginning
- `<cb n="a" facs="#b_84r-a"/>` - Column beginning
- `<lb n="1"/>` - Physical line beginning

**Critical Rule**: These elements are placed as high as possible in the XML hierarchy:
- Between verse groups (`<lg>`) when possible
- Between verses (`<l>`) when verses span pages
- Inside words when continuous text spans lines

### 4.2 Divisions and Sections
```xml
<div ana="hc:Section" xml:id="section_1">
    <head xml:id="head_1">
        <hi hei:color="Red">Erster Streich</hi>
    </head>
    <!-- verse groups -->
</div>
```

### 4.3 Verse Structure
**Line Groups** (`<lg>`):
```xml
<lg ana="hc:Couplet">  <!-- or hc:Tercet, hc:Quatrain -->
    <l n="2126.251" hei:altN="5" xml:id="l_2126.251">...</l>
    <l n="2126.252" hei:altN="6" xml:id="l_2126.252">...</l>
</lg>
```

**Line Attributes**:
- `@n` - Standard edition verse number (e.g., "123", "123a", "123.1" for added verses)
- `@xml:id` - Unique identifier for synchronization (e.g., "l_123", "l_123a", "l_123.1")
- `@hei:altN` - Alternative numbering (sequential count in this manuscript)

**Additional Verse Numbers**:
- Inserted verses: Use letter suffixes (`123a`) or decimal notation (`123.1`)
- `@xml:id` uses dots not commas (XML requirement): `l_123.1` not `l_123,1`

---

## 5. Word-Level Tokenization

### 5.1 Core Concept
**Every linguistic word** is tagged as `<w xml:id="w_VERSE_POSITION">`:

```xml
<l n="2126.251" xml:id="l_2126.251">
    <lb n="5"/>
    <w xml:id="w_2126.251_1">co<choice><am>&bar;</am><ex>m</ex></choice></w>
    <c> </c>
    <w xml:id="w_2126.251_2"><choice><orig>v</orig><reg>u</reg></choice>ne</w>
    <c> </c>
    <w xml:id="w_2126.251_3">beſte</w>
</l>
```

### 5.2 Spatium Handling
**Critical Feature**: Explicit space encoding with `<c> </c>`

**Rationale**:
- Manuscripts have inconsistent spacing
- Allows independent control of:
  - Transcription view (diplomatic: as written)
  - Edition view (normalized: editorial spacing)

**Usage**:
```xml
<!-- Separate words in manuscript -->
<w>ze</w><c> </c><w>lesen</w>

<!-- Joined words in manuscript, editorial separation -->
<w>ze</w><choice><orig/><reg><c> </c></reg></choice><w>lesen</w>

<!-- Separate in manuscript, editorial joining -->
<w>ge<choice><orig><c> </c></orig><reg/></choice>lesen</w>
```

### 5.3 Word Tokenization Rules
From handbook:

1. **Pronominal adverbs**: Always separate
   - `daran` → `<w>dar</w><w>an</w>`

2. **Separable verb prefixes**: Always separate
   - `abebrechen` → `<w>abe</w><w>brechen</w>`

3. **Contractions** (Proklise/Enklise/Krasis): Separate components
   - `sageter` → `<w>saget</w><w>er</w>` (= sagete er)
   - `zen` → `<w>z</w><w>en</w>` (= ze den)
   - `destwar` → `<w>de</w><w>st</w><w>war</w>`

4. **Numbers**: Use `<num value="12">xii</num>`

### 5.4 Line Breaks within Words
```xml
<w>vrüme<metamark ana="hc:Hyphen">⸗</metamark><lb n="27" break="no"/>keit</w>
```

---

## 6. Abbreviations and Expansions

### 6.1 Editorial Expansion
```xml
<choice>
    <am>&bar;</am>      <!-- abbreviation mark (entity) -->
    <ex>m</ex>          <!-- expansion -->
</choice>

<!-- In context -->
<w>co<choice><am>&bar;</am><ex>m</ex></choice></w>  <!-- "cōm" = "com" -->
```

### 6.2 Complex Abbreviations
```xml
<choice>
    <seg ana="hc:AbbreviatedTokenSegment">
        t<am>&er;</am>  <!-- "ter" mark -->
    </seg>
    <seg ana="hc:ExpandedTokenSegment">
        <ex>r</ex>a     <!-- expanded form -->
    </seg>
</choice>
```

---

## 7. Gaps, Damage, and Illegibility

### 7.1 Gap Types
**Different rendition values**:

```xml
<!-- Text is lost/missing -->
<gap rendition="hc:Lost" unit="leaf" extent="unknown">
    <desc>Missing approximately 12-13 folios</desc>
</gap>

<!-- Text is cut off (damaged edge) -->
<gap rendition="hc:CutOff" unit="character" extent="unknown"/>

<!-- Text is faded but potentially recoverable -->
<gap rendition="hc:Faded" unit="line" quantity="1"/>

<!-- Text is illegible -->
<gap rendition="hc:Illegible" unit="character" extent="unknown"/>
```

### 7.2 Damage within Words
```xml
<w xml:id="w_1_1">
    <gap rendition="hc:CutOff" unit="character" extent="unknown"/>
    <damage rendition="hc:Faded">enu</damage>
</w>
```

### 7.3 Blank Space for Missing Content
```xml
<choice>
    <orig>
        <space rendition="hc:BlankAreaLeftForInitial" unit="character" quantity="1">
            <desc xml:lang="de">Aussparung für Initiale</desc>
        </space>
    </orig>
    <supplied><hei:initial>S</hei:initial></supplied>
</choice>
```

---

## 8. Scribal Corrections

### 8.1 Additions
```xml
<!-- Letter added above line -->
<w>so<add hei:placeRef="hc:AboveLine">l</add></w>

<!-- Word added in margin -->
<add hei:placeRef="hc:ColumnMarginRight"><w>neu</w></add>
```

### 8.2 Deletions
```xml
<!-- Letter deleted (underdotted) -->
<w>leit<del rendition="hc:Underlined">e</del></w>

<!-- Word deleted (struck through) -->
<del rendition="hc:Strikethrough"><w>überflüssig</w></del>
```

**Deletion Methods**:
- `hc:Erased` - Scraped off
- `hc:Strikethrough` - Line through
- `hc:RedStrikethrough` - Red line
- `hc:Overwritten` - Written over
- `hc:Overpainted` - Painted over
- `hc:Underlined`, `hc:Underdotted`, `hc:Overdotted` - Marked for deletion
- `hc:Adapted` - Letter adapted/changed

### 8.3 Substitutions
```xml
<!-- Letter replaced -->
<w>w<subst>
    <del rendition="hc:Underdotted hc:Overdotted">o</del>
    <add hei:placeRef="hc:AboveLine">a</add>
</subst>rt</w>

<!-- Words replaced -->
<subst>
    <del rendition="hc:Erased">
        <w>falsche</w><c> </c><w>Wörter</w>
    </del>
    <add hei:placeRef="hc:Superimposed">
        <w>richtige</w><c> </c><w>Wörter</w>
    </add>
</subst>
```

### 8.4 Multi-Element Substitutions
When deletion and addition are not adjacent:
```xml
<substJoin target="#del_162_3 #del_162_4_1 #add_162_4_1 #add_162_6"/>
```

---

## 9. Visual Features

### 9.1 Initials
```xml
<hei:initial rendition="hc:Lombard"
             hei:color="Red"
             hei:heightLines="3"
             xml:id="initial_37">S</hei:initial>
```

**Initial Types**:
- `hc:Lombard` - Lombard capital
- `hc:FlourishInitial` - Fleuronné
- `hc:SilhouetteInitial` - Silhouette
- `hc:ScrollworkInitial` - Vine/scroll decoration
- `hc:FigureInitial`, `hc:HistoriatedInitial` - Figural/narrative
- `hc:Sketch` - Drawn but not completed

**Cues for Initials**:
```xml
<hei:cue ana="hc:CueInitial"
         hei:placeRef="hc:InSpace"
         target="#initial_37"><c>d</c></hei:cue>
```

### 9.2 Highlighting
```xml
<!-- Colored text -->
<hi hei:color="Red">Von künig Artus</hi>

<!-- Red stroke at verse beginning (typical in paper MSS) -->
<hi rendition="hc:RedStroke">D</hi>as

<!-- Versal (protruding letter) -->
<hi rendition="hc:Versal">W</hi>er

<!-- Cadel (decorative but not initial) -->
<hi rendition="hc:Cadel">M</hi>ancher
```

### 9.3 Section Markers
```xml
<lb n="7"/>
<label ana="hc:SectionMarker" hei:placeRef="hc:PageMarginLeft"><c>¶</c></label>
<l n="12">
    <w xml:id="w_1234_1"><seg ana="hc:EditorialEmphasis">N</seg>u</w>
    <!-- First letter gets editorial emphasis in edition view -->
</l>
```

### 9.4 Punctuation
```xml
<!-- Reimpunkt (point on middle line) -->
<w>ende</w><pc>·</pc><c> </c><w>swer</w>

<!-- Multiple marks -->
<pc>.</pc><pc>/</pc>
```

---

## 10. Marginal Content and Zones

### 10.1 Zone Transitions
```xml
<!-- Begin marginal zone -->
<milestone ana="hc:ZoneBeginning" facs="#b_84v-b"/>
<note xml:id="note_1" ana="hc:Gloss">Nota: Hühner</note>

<!-- Return to main zone -->
<milestone ana="hc:ZoneShift" facs="#b_84v-a"/>
```

### 10.2 Notes and Glosses
```xml
<note xml:id="note_1" ana="hc:Gloss">Nota bene</note>
<note ana="hc:EditorialContent">Editorial explanation...</note>
```

### 10.3 Quire Signatures and Catchwords
Recorded in marginal zones with specific placement:
```xml
<zone ana="hc:MarginalZone"
      xml:id="b_12v-c"
      hei:placeRef="hc:PageBottom hc:PageMarginRight"/>
```

---

## 11. Line Overflow

### 11.1 Run-Over Lines
When a verse overflows to another line:

```xml
<l n="419">
    <lb n="26"/>
    <w>...</w><w>...</w><w>...</w>
    <c> </c>
    <milestone ana="hc:LineSegmentBeginning hc:RunOverBelow"
               n="2"
               hei:belongsToLine="27"/>
    <w>overflow</w><w>text</w>
</l>
```

**Run-Over Types**:
- `hc:RunOverBelow` - Continues below
- `hc:RunOverAbove` - Continues above
- `hc:RunOverMark` - Mark connecting segments (e.g., `|`)

### 11.2 Interlinear Lines
```xml
<lb n="26.1" ana="hc:InterlinearLine hc:RunOverAbove"
    rendition="hc:FlushRight"/>
```

---

## 12. Editorial Regularization

### 12.1 Orthographic Normalization
```xml
<!-- u/v regularization -->
<w><choice><orig>v</orig><reg>u</reg></choice>ne</w>

<!-- Letter substitution -->
<w>a<choice><orig>u</orig><reg>v</reg></choice>um</w>
```

### 12.2 Editorial Interventions
```xml
<choice>
    <orig><!-- diplomatic transcription --></orig>
    <reg><!-- regularized form --></reg>
</choice>
```

**Common Uses**:
- Letter normalization (u/v, i/j)
- Spacing adjustments
- Punctuation editing
- Capitalization

---

## 13. Complex Features

### 13.1 Transpositions
When scribe changes verse order with marks:
```xml
<metamark ana="hc:TranspositionMark">a</metamark>
```
Verses tagged in physical order, numbers reflect logical order.

### 13.2 Verse Replication
```xml
<l n="897" xml:id="l_897" hei:replicates="#l_23">...</l>
```

### 13.3 Verse Correspondence
For intentionally similar verses:
```xml
<l n="23" xml:id="l_23" corresp="#l_897">...</l>
```

### 13.4 Figures
```xml
<milestone ana="hc:ZoneBeginning" facs="#B_44r-b"/>
<figure n="1">
    <figDesc>Zeichnung eines Falken in roter Tinte</figDesc>
    <note ana="hc:EditorialContent">Description...</note>
</figure>
```

---

## 14. Metamarks

Special signs with semantic function:
```xml
<metamark ana="hc:Hyphen">⸗</metamark>        <!-- word break -->
<metamark ana="hc:RunOverMark">|</metamark>   <!-- line continuation -->
<metamark ana="hc:WordDivider">·</metamark>   <!-- word separator -->
<metamark ana="hc:CorrectionMark">^</metamark> <!-- correction -->
<metamark ana="hc:InsertionMark">,</metamark>  <!-- insertion point -->
<metamark ana="hc:DecorativeMark">❦</metamark> <!-- decoration -->
<metamark ana="hc:WordMark">|</metamark>      <!-- single-letter word marker -->
<metamark ana="hc:NumberMark">·</metamark>    <!-- numeral marker -->
```

---

## 15. Character Encoding

### 15.1 Special Characters
Uses **MUFI (Medieval Unicode Font Initiative)** entities:
```xml
&bar;    <!-- macron/overbar for abbreviation -->
&us;     <!-- -us abbreviation mark -->
&er;     <!-- -er abbreviation mark -->
```

### 15.2 Long s
**Critical**: Schaft-s `ſ` is preserved (not normalized to `s`), since medieval scribes confused it with `f`.

---

## 16. Document Variants Observed

### 16.1 Max und Moritz A
**Features**:
- Simple two-column layout
- Zone transitions for marginal notes
- Basic `<div>` sections
- Trailing incomplete sections

### 16.2 Max und Moritz B
**Additional Features**:
- Verse transpositions (verses appear in different order)
- Additional verses (20a between 20 and 21)
- Multiple `<label>` elements for subdivisions
- Starts mid-page (`<pb n="1"/><cb n="b"/><lb n="15"/>`)

### 16.3 Gregoire Fragment
**Advanced Features**:
- Extensive use of `<gap>` elements (manuscript damage)
- Cut-off text at line beginnings
- Faded and illegible sections
- Complex abbreviations with specialized segments
- Dual page structure (recto/verso)
- Horizontal layout zones

---

## 17. Key Concepts for Testing

### 17.1 Hierarchical Placement
**Critical Rule**: Empty elements (`<pb>`, `<cb>`, `<lb>`, `<milestone>`) placed as high as possible:
- Between `<lg>` groups
- Between `<l>` lines
- Inside `<w>` words only when necessary

### 17.2 ID System
**Consistent naming**:
- Verses: `l_` + verse number
- Words: `w_` + verse number + `_` + position
- Elements: element name + `_` + context number

### 17.3 Ontology Integration
All `ana` attributes reference the **heiEDITIONS Concepts** ontology:
- `hc:` prefix resolves to `https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/`
- Provides semantic typing for all editorial decisions

### 17.4 Dual View Architecture
**Core concept**: Single source, multiple presentations:
- **Transcription view**: Diplomatic, preserves manuscript features
- **Edition view**: Normalized, applies editorial regularizations
- Achieved via `<choice>`, `<orig>`, `<reg>` elements

---

## 18. Testing Implications

### 18.1 Essential Test Fixtures Needed

1. **Basic verse structure**
   - Simple couplets with line breaks
   - Word tokenization with spaces
   - Page/column/line markers

2. **Abbreviations**
   - Various `<choice>` constructions
   - Entity resolution
   - Segment-level expansion

3. **Scribal corrections**
   - Add/del/subst combinations
   - Multi-word deletions with spaces
   - Adapted letters

4. **Damaged text**
   - Gaps of various types
   - Faded/illegible sections
   - Cut-off text

5. **Complex layout**
   - Multi-column pages
   - Zone transitions
   - Marginal content
   - Run-over lines

6. **Visual features**
   - Initials with cues
   - Highlighting (color, rendition)
   - Section markers

7. **Editorial content**
   - Orig/reg choices
   - Supplied text
   - Editorial notes

### 18.2 Transformation Scenarios

Based on analyzed steps in `step_library.py`:

1. **Delete elements**: Remove notes, form work, etc.
2. **Unwrap elements**: Convert `<choice>` to single option
3. **Add attributes**: Mark elements for processing
4. **Transform structure**: Flatten hierarchies
5. **Regularize text**: Apply editorial choices
6. **Extract information**: Pull specific content types

### 18.3 Critical Edge Cases

1. **Empty elements**: `<w/>`, `<c> </c>`, `<seg/>`
2. **Nested corrections**: `<w>...<subst><del>...<add>...</add></del></subst>...</w>`
3. **Cross-element gaps**: `<gap>` spanning multiple words
4. **Zone boundaries**: Content split across zones
5. **Whitespace sensitivity**: Exact preservation in `<c>` elements
6. **Namespace mixing**: TEI + hei: elements

---

## 19. Recommendations for Test Suite

### 19.1 Fixture Categories

**Level 1 - Minimal** (current):
- Basic TEI structure
- Simple verse groups
- Word tokenization

**Level 2 - Intermediate** (needed):
- Abbreviations and expansions
- Scribal corrections
- Page/column structure
- Marginal content

**Level 3 - Advanced** (needed):
- Damaged manuscript fragments
- Complex layout with zones
- Run-over lines
- Visual features (initials, highlighting)

**Level 4 - Production-like** (needed):
- Real manuscript fragments (like Gregoire example)
- Multiple witnesses for comparison
- Full editorial apparatus

### 19.2 Fixture Naming Convention
```
tests/fixtures/
├── minimal/          # Current simple fixtures
├── intermediate/     # Medium complexity
│   ├── abbrev_*.xml
│   ├── corrections_*.xml
│   ├── multicolumn_*.xml
│   └── marginal_*.xml
├── advanced/         # Complex features
│   ├── damaged_*.xml
│   ├── layout_*.xml
│   └── visual_*.xml
└── production/       # Real-world examples
    ├── gregoire_fragment.xml
    ├── hartmann_excerpt.xml
    └── comparative_*.xml
```

### 19.3 Test Data Principles

1. **Whitespace preservation**: Critical for this project
2. **Namespace awareness**: Both default TEI and hei: extension
3. **Entity handling**: MUFI characters in fixtures
4. **Validation**: All fixtures should be schema-valid
5. **Documentation**: Each fixture should have README explaining features tested

---

## 20. Summary Statistics

### Document Complexity Metrics

| Feature | Max A | Max B | Gregoire | Typical |
|---------|-------|-------|----------|---------|
| Pages | 2 | 2 | 2 | 20-200 |
| Columns/page | 1 | 1 | 2 | 1-2 |
| Verses | 32 | 32 | ~200 | 5000-10000 |
| Line groups | 24 | 26 | ~100 | 2500-5000 |
| Added verses | 0 | 1 | Many | Variable |
| Transposed verses | 0 | 2 | Unknown | Variable |
| Gaps | 0 | 0 | ~30 | Variable |
| Corrections | 0 | 0 | ~10 | Variable |
| Marginal notes | 2 | 1 | 0 | Variable |
| Abbreviations | 0 | 0 | ~50 | High |
| Initials | 2 | 2 | 0 | Variable |

**Conclusion**: The Gregoire fragment, despite being short, contains the most "production-like" complexity with damaged text, abbreviations, and advanced features. It should serve as a model for creating realistic test fixtures.
