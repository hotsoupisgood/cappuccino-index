CAFÉ DENSITY BY CITY — sourced to test James's "competition" claim
====================================================================
(claim: Australia/Italy have low Cappuccino Index partly because of high
café competition/density; and specifically re: London vs Edinburgh —
"you'd need information about number of outlets... and population
densities. Hard to prove or disprove" — see transcripts/cappuccino_index_transcript.txt)

WHAT WAS DONE
-------------
1. Checked for an existing dataset with café counts. None exists in this
   project (full_data.csv has wage/price/urban-classification only, no
   outlet counts). Checked secondary sources (IBISWorld, World Coffee
   Portal/Allegra, marketing blogs) — numbers exist but are inconsistent,
   partly paywalled, and don't share a common methodology across
   countries, so they can't be compared apples-to-apples.

2. Pulled café counts directly from OpenStreetMap via the public Overpass
   API (free, no key required, reproducible). Query template used for
   every area:

     [out:json][timeout:T];
     area["name"="<AREA_NAME>"]["boundary"="administrative"]["admin_level"="<LEVEL>"]->.a;
     (
       node(area.a)[amenity=cafe];
       way(area.a)[amenity=cafe];
     );
     out count;

   Sent via: curl -s "https://overpass-api.de/api/interpreter" \
             -H "User-Agent: cappuccino-index-research/1.0" \
             --data-raw '<query above>'

   Each area's exact OSM boundary relation (name/admin_level, or GSS/wikidata
   code for disambiguation) was confirmed first with a diagnostic query
   (`rel["name"="..."]["boundary"="administrative"];out tags;`) before
   counting, because plain name matches are ambiguous (e.g. there are ~15
   places called "Roma" in OSM, and multiple "Manchester"s worldwide).
   Manchester was targeted by its ONS GSS code (E08000003) for that reason.

3. Divided each count by an official population figure (ONS / ABS / ISTAT,
   sourced separately by web search, cited per row below) to get people-
   per-café and cafés-per-10,000-residents.

RESULTS (full detail in cafe_density_by_city.csv)
---------------------------------------------------
area                                            cafes   population  ppl/cafe  per_10k
City of Melbourne (LGA, inner-city core only)     640      177,396       277    36.08
Brighton and Hove (council area)                  406      283,870       699    14.30
City of Edinburgh (council area)                  722      530,680       735    13.61
Milano (comune)                                  1779    1,371,850       771    12.97
Greater London Authority                         6803    8,950,000     1,316     7.60
Manchester (metropolitan borough)                 336      551,938     1,643     6.09
Napoli (comune)                                   484      911,697     1,884     5.31

Population sources: ONS mid-year LA estimates (Edinburgh, London, Brighton
& Hove); 2021 UK Census (Manchester); ABS Estimated Resident Population,
30 Jun 2023 (Melbourne); ISTAT resident population 2024 (Milano, Napoli).

KEY FINDING RE: THE LONDON vs EDINBURGH CLAIM
-----------------------------------------------
Both "Greater London" and "City of Edinburgh" are whole-city administrative
boundaries (not just a CBD core), so this is the one clean apples-to-apples
comparison in the set. Result: Edinburgh has ~1.8x London's café density per
capita (13.6 vs 7.6 per 10,000 people), even though London has vastly more
cafés in absolute terms (6,803 vs 722).

James's theory predicts the opposite: he calls London the UK's "most
competitive coffee scene" and expects that to track its lowest (most
"competitive-looking") index, with Edinburgh — highest index in the UK
survey — implicitly the least dense/competitive. The actual density data
says Edinburgh is denser, not sparser. This is real evidence against the
density-drives-competition-drives-index mechanism, at least as measured by
raw café count per capita — exactly the test he said would be "hard to
prove or disprove."

CAVEATS / WHAT DIDN'T GET VALIDATED
------------------------------------
- Rome, Sydney, and Brisbane counts were NOT obtained — overpass-api.de
  rate-limited then temporarily blocked this session's IP after the burst
  of queries (see osm_cafe_counts_raw.json "failed_no_data_obtained" for
  the exact errors). Melbourne stands in as the only Australian data
  point and Milano/Napoli as the only Italian ones; the original "does
  Australia/Italy as countries have unusually dense coffee scenes" question
  is only partially answered.
- City of Melbourne and (if re-run) City of Sydney/Brisbane are small
  inner-city LGAs (Australian capital cities are governed by many small
  councils, not one unified city government the way London has "Greater
  London"), NOT full metro-region boundaries. Melbourne's 36 cafés/10k
  figure is therefore not directly comparable to Greater London's 7.6 —
  it's comparing a dense inner core to an entire metro region. A fair
  Australia vs UK/Italy comparison would need consistently-defined
  boundaries (either all full metro areas, or all city-centre cores).
- OSM's amenity=cafe tag is comprehensive (includes chains, hotel cafés,
  bakery-cafés, tearooms) and is community-mapped, so absolute counts
  can differ substantially from press/industry figures that use narrower
  definitions or different boundaries — e.g. a 2026 marketing-blog "study"
  cited elsewhere in this research put Edinburgh at "over 200" coffee
  shops and London at 3,718 total cafés, both well below the OSM counts
  here (722 and 6,803). Treat cross-source absolute counts with caution;
  the within-methodology relative comparison (Edinburgh > London per
  capita) is the trustworthy part, since it used one consistent method.
- Mapping completeness varies by region — southern Italy (Napoli) may be
  less thoroughly mapped in OSM than northern Italy (Milano) or the UK,
  which could partly explain Napoli's low count rather than genuinely
  fewer cafés.

TO EXTEND THIS
---------------
Re-run the same query template for Roma/Sydney/Brisbane (and any other
city) once the Overpass rate limit clears — wait a while before retrying,
or use a different Overpass mirror (e.g. overpass.kumi.systems) with
requests spaced several seconds apart to avoid getting blocked again.
