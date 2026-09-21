# Research: External Claims Check

Compiled 2026-09-14. Every claim below is about an outside organisation, dataset or piece of
science, checked against a primary source on that date. Project docs were used as leads only.
All URLs accessed 2026-09-14. No em dashes; plain hyphens only.

Box = 45-100 E, 10 S-25 N. Window opens 2025-08-10.

## Summary

| # | Claim | Where | Verdict | Fix |
| --- | --- | --- | --- | --- |
| 1 | No maintained pure-Python WCS server; OPeNDAP is what the community uses | requirements.html:584, CONTEXT.md:307, README-full.md:364, 673 | PARTLY | Reword (below) |
| 2 | Thirty-six analyses is not a training set | requirements.html:586 | HOLDS | - |
| 3 | Newest GO-SHIP section in the box is April 2025 | requirements.html:589, README-full.md:341, 681 | HOLDS | - |
| 4 | HF-radar/ADCP behind a login at services.incois.gov.in, which does not resolve | requirements.html:591 | WRONG | Reword |
| 5 | LAS catalogue reads; OPeNDAP returns zero bytes | requirements.html:593 | HOLDS | - |
| 6 | Godas ends 2025-05-22 | requirements.html:595 | PARTLY | Say it is INCOIS's LAS copy |
| 7 | Newest glider cast in the box is 2022-10-14 | requirements.html:598, CONTEXT.md:286, 321 | HOLDS | - |
| 8a | Kessler-McCreary analysis is built from Argo; moored buoys are independent | explore.ts:125, guide.ts:880, README.md:68 | HOLDS | - |
| 8b | Same for the VAM analysis | same | UNVERIFIABLE | - |
| 9 | ERDDAP value-added series ended 2019-03-30 | CONTEXT.md:10, requirements.html:351 | HOLDS | - |
| 10 | INCOIS still publish TCHP and MLD maps | CONTEXT.md:10, README-full.md:270 | HOLDS | - |
| 11 | INCOIS's own Argo archive ends 2025-04-23 | provenance.html:353 | HOLDS | - |
| 12 | INCOIS ERDDAP already serves WMS for temperature | README-full.md:364 | HOLDS | - |
| 13 | Copernicus reanalysis 001_030 ends 2026-06-23 | adr/0013:38 (docs/NUMBERS.md:35 says 2022) | HOLDS | "2022" is wrong |
| 14 | Copernicus publish uo and vo and no w; nobody publishes vertical velocity | CONTEXT.md:317, adr/0017:13, README.md:353, README-full.md:677, DECK.md:543 | WRONG | Reword |
| 15 | INCOIS publish no current vectors | CONTEXT.md:317 | PARTLY | Reword |
| 16 | About 4,000 Argo floats | explore.ts:197 | HOLDS | - |
| 17 | Each float sinks to 2 km and drifts ten days | explore.ts:197-198 | PARTLY | Reword |
| 18 | SARAT exists; a real search needs wind and object drift | explore.ts:156-157 | HOLDS | - |
| 19 | Bay of Bengal 3.0 kg/m3 lighter, 3.7 PSU fresher | explore.ts:182, guide.ts:287-288, README-full.md:69, 71, 131 | HOLDS | - |
| 20 | Above 60 kJ/cm2 is the usual threshold for rapid intensification | guide.ts:211, 373; index.html:826; README-full.md:75 | PARTLY | Reword and attribute |
| 21 | TCHP by Leipper and Volgenau, heat above 26 degC to that isotherm | guide.ts:943 | HOLDS | - |
| 22 | 26 degC is the conventional floor for cyclone development | guide.ts:390 | HOLDS | - |
| 23 | de Boyer Montegut: 0.03 kg/m3, 0.2 degC, 10 m | guide.ts:409, 425, 947 | HOLDS | - |
| 24 | WOA23: 1991-2020, 1 degree, monthly, to 1500 m | CONTEXT.md:150, requirements.html:752 | HOLDS | - |
| 25 | Montha: D 25 Oct, SCS 28 Oct, 50 kt, crossed near Narsapur 28 Oct, weakened 30 Oct | ppt/PLAN.md:20, cases.ts | HOLDS | - |
| 26 | PS 26067 names the EGO glider FTP; theme Disaster Management; Software | README.md:189, requirements.html:380 | HOLDS | - |
| 27 | NOAA OSMC GTS feed, public domain | README-full.md:730 | HOLDS | - |
| 28 | Ifremer Argo ERDDAP | README-full.md:365 | HOLDS | - |
| 29 | RAMA is "the joint MoES-NOAA array" | guide.ts:879 | PARTLY | Reword |
| 30 | OMNI run by NIOT, INCOIS as data centre | guide.ts:878 | HOLDS | - |
| 31 | PS deadline 20 September 2026 | ppt/PLAN.md:24, ppt/NOTES.md:216 | WRONG | 30 September 2026 |

Count: 22 HOLDS, 3 WRONG, 6 PARTLY, 1 UNVERIFIABLE.

---

## Priority 1: the "not built" table

### 1. OGC WCS - PARTLY

"No maintained pure-Python server, and OPeNDAP is what this community actually uses." (requirements.html:584-585; same idea CONTEXT.md:307-308, README-full.md:364, 673-674)

- pygeoapi 0.24.0, released 2026-07-28, pure Python, maintained, has an xarray provider for
  NetCDF/Zarr - but it implements **OGC API - Coverages**, the successor to WCS, not classic WCS.
  https://pypi.org/project/pygeoapi/ and https://docs.pygeoapi.io/en/stable/publishing/ogcapi-coverages.html
- EOxServer 1.5.3 (PyPI upload 2025-05-06) is a Python WCS 2.0 server, but its dependencies
  include `mapscript==8.0.*` and `gdal`, i.e. it runs on MapServer. Maintained, not pure Python.
  https://pypi.org/pypi/EOxServer/json
- THREDDS implements WCS 1.0.0, enabled by default (Java).
  https://docs.unidata.ucar.edu/tds/current/userguide/wcs_ref.html
- INCOIS ERDDAP (version 2.30) returns 404 on `/erddap/wcs/index.html`; its dataset list offers
  griddap, tabledap and WMS. https://erddap.incois.gov.in/erddap/wcs/index.html
- No xpublish WCS plugin found in search.
- OPeNDAP as the norm: true of NOAA PSL THREDDS (answered today, see 6) and INCOIS ERDDAP griddap.
  **Not** true of Copernicus Marine: "Since April 2024, the old services MOTU, OPeNDAP, ERDDAP,
  FTP and WMS no longer exist." https://help.marine.copernicus.eu/en/articles/8612591-switching-from-old-to-new-services

"No maintained pure-Python WCS server" holds narrowly. "What this community actually uses" is too
broad, since the largest European provider dropped OPeNDAP.

### 2. Machine learning - HOLDS (judgement)

"Thirty-six analyses is not a training set." (requirements.html:586-587)

DINCAE 1.0, a neural gap-filler for SST, trained on 5,266 daily images over 25 years
(1985-2009). https://gmd.copernicus.org/articles/13/1609/2020/ . Thirty-six fields is two orders of
magnitude smaller. Defensible.

### 3. Ship CTD - HOLDS

"Newest GO-SHIP section in this box is April 2025, four months before the window opens." (requirements.html:589-590)

CCHDO full cruise list (https://cchdo.ucsd.edu/api/v1/cruise/all, 2,558 cruises, newest start
2026-05-11), filtered to track points inside the box and start after 2023-01-01, gives two:
- `325020250321`, R/V Thomas G. Thompson, GO-SHIP line **I09N**, 2025-03-21 to 2025-04-27, 76 track points in the box. https://cchdo.ucsd.edu/cruise/325020250321
- `33RR20230629`, R/V Roger Revelle, GO-BGC (not GO-SHIP), 2023.

Nothing after April 2025. End date to window is about three and a half months, so "four months" is
rounded.

### 4. HF-radar and ADCP - WRONG

"India's are behind a login at `services.incois.gov.in`, which does not resolve." (requirements.html:591-592)

- `nslookup services.incois.gov.in 8.8.8.8` returns **172.16.1.134**, a private (RFC 1918)
  address. It resolves; it cannot be reached. `curl https://services.incois.gov.in/` timed out
  at 20 s.
- `odis.incois.gov.in` (where search results place the HF radar page) does not resolve on the
  local resolver. `incois.gov.in/portal/datainfo/hfradar.jsp` returns 404.
- Access terms, from INCOIS staff in a peer-reviewed paper: "A user request form is provided to
  each user irrespective of whether is data open or restricted", and "Any data within the
  Exclusive Economic Zone (EEZ) is generally restricted." Coastal HF radar is inside the EEZ.
  https://datascience.codata.org/articles/10.5334/dsj-2018-011
- A "login" specifically could not be confirmed.

### 5. INCOIS LAS - HOLDS (still behaves so)

"The catalogue reads fine; the OPeNDAP endpoint returned zero bytes at 90 s and again at 240 s." (requirements.html:593-594)

The past measurement cannot be re-run; today's behaviour matches it.
- https://las.incois.gov.in/thredds/catalog/las/catalog.xml : 200, lists 59 datasets (Argo 10-day and monthly, value-added products, ArgoSST, Godas 2022-2025, BIO-ROMS pCO2, Levitus).
- `.../thredds/dodsC/las/levitus_climatology_cdf/data_levitus_climatology.jnl.dds` and `.../id-fe1698c540/data_home_las_datasets_godas_2022.nc.jnl.dds`: **0 bytes at 240 s**, both.
- `.../id-cbbdd5ab07/data_home_las_datasets_godas_2025.nc.jnl.ascii?TIME`: 0 bytes at 120 s.
- Port 80 refused; https://las.incois.gov.in/las/ returns only a "LAS Redirect" page.

### 6. Godas - PARTLY

"Ends 2025-05-22, under three months before the window opens." (requirements.html:595-596)

- The lead (docs/plan/04:76) shows this is INCOIS's **LAS copy**, `Godas 2025`. It is in the LAS
  catalogue today, but its time axis could not be read (item 5), so 2025-05-22 is not
  re-verified.
- NOAA's own Godas does not end there. PSL listing https://downloads.psl.noaa.gov/Datasets/godas/
  has `pottmp.2026.nc` (modified 2026-08-17). Its OPeNDAP time axis
  (https://psl.noaa.gov/thredds/dodsC/Datasets/godas/pottmp.2026.nc.ascii?time, days since
  1800-01-01) is 7 monthly means, January to **July 2026**. The 2025 file has all 12 months.
  Grid 360 x 418, 40 levels.
- CPC Godas pages not checked.

The table row reads as "Godas ends", which NOAA's copy contradicts.

### 7. Glider - HOLDS

"The newest cast in this box is 2022-10-14." (requirements.html:598)

Streamed the full index, ftp://ftp.ifremer.fr/ifremer/glider/v2/glider_prof_index.txt
(Content-Length 248,440,873; Last-Modified **2026-09-14 06:36 GMT**, i.e. updated today), through
a box filter: 824,632 data rows, **2,876** in the box, all WMO 2801950, newest date **20221014**,
zero after 2022-10-14.

---

## Priority 2

### 8a/8b. INCOIS Argo analyses and the moored buoys - HOLDS (Kessler-McCreary), UNVERIFIABLE (VAM)

"INCOIS assimilate Argo, so a float largely shows the model agreeing with itself. The moored buoys are the independent check." (explore.ts:125-126); "INCOIS do not feed these into the analysis" (guide.ts:880)

- INCOIS Technical Report INCOIS-MOG-ARGO-TR-04-2007 v2.0 (Udaya Bhaskar et al.), the Kessler-McCreary objective analysis: "The data used for generating the gridded product consisted of all the CTD data measured by Argo floats in the Indian Ocean region", and "Subsurface data from these buoys [OMNI, RAMA] are also used for independent validation of the gridded product." https://argo.ucsd.edu/wp-content/uploads/sites/361/2020/05/Incois_Argo_ObjectiveAnalysis_Ver2.0.pdf
- The report is dated 2007 (revision 2014). The ERDDAP metadata for `incois_argo_10day_McCreary` and `incois_argo_10d_VAM` names no inputs. No method document for VAM was found, and the bake reads VAM.
- Wording note: this is objective analysis (gridding), not data assimilation into a model. "Grid Argo" or "are built from Argo" is more exact than "assimilate".

### 9. ERDDAP value-added series ended 2019-03-30 - HOLDS

https://erddap.incois.gov.in/erddap/info/incois_valueadded_products_datasets/index.csv :
`time_coverage_end 2019-03-30T00:00:00Z`, start 2004-01-10. Variables MLD, ILD, D26, D20, HTCNT,
DYN_HT, **GEO_U, GEO_V**.

### 10. INCOIS still publish TCHP and MLD - HOLDS

- https://incois.gov.in/site/services/tchp.jsp : TCHP shown from ROMS (forecast), HYCOM (forecast) and **GODAS (analysis)**. No date stamp.
- https://incois.gov.in/oceanservices/rsmc_ocean.jsp : RSMC product list includes Mixed Layer Depth and TCHP.

"From their forecast models" is right but incomplete: an analysis is shown too.

### 11. INCOIS Argo archive ends 2025-04-23 - HOLDS

https://erddap.incois.gov.in/erddap/tabledap/Indian_ARGO_Floats.csv?time&orderByMax("time") returns `2025-04-23T13:28:00Z`.

### 12. INCOIS ERDDAP serves WMS for temperature - HOLDS

The ERDDAP dataset list gives a WMS endpoint for `incois_argo_10d_VAM` and the other Argo analyses. https://erddap.incois.gov.in/erddap/info/index.csv

### 13. Copernicus GLOBAL_MULTIYEAR_PHY_001_030 end - HOLDS (2026-06-23)

STAC https://stac.marine.copernicus.eu/metadata/GLOBAL_MULTIYEAR_PHY_001_030/product.stac.json :
temporal interval 1993-01-01 to **2026-06-23**. The daily dataset `cmems_mod_glo_phy_my_0.083deg_P1D-m_202311` shows the same range, `admp_updated_data` 2026-07-20. "Ends in 2022" (docs/NUMBERS.md:35) is out of date. The product lists no separate `myint` dataset, so a separate interim end date could not be found.

### 14. Vertical velocity - WRONG

"Copernicus publish `uo` and `vo` and no `w`" (CONTEXT.md:317); "The Copernicus product this platform reads publishes `uo` and `vo` and no `w`" (adr/0017:13); "Nobody publishes vertical velocity for this region" (README.md:353); "neither provider publishes one" (README-full.md:678); "neither provider publishes a vertical velocity" (ppt/DECK.md:543)

STAC https://stac.marine.copernicus.eu/metadata/GLOBAL_ANALYSISFORECAST_PHY_001_024/product.stac.json lists `cmems_mod_glo_phy-wcur_anfc_0.083deg_P1D-m_202406` (also P1M). Its variable is `wo`, "Ocean vertical velocity", standard name `upward_sea_water_velocity`, m s-1. Product interval 2019-01-01 to 2026-09-24. The dataset this platform reads (`-cur_`) has only uo/vo, but the product publishes w, and so does the reanalysis family. It is a model output, not a measurement, so the refusal can stand on that ground.

### 15. INCOIS publish no current vectors - PARTLY

"INCOIS publish neither" (CONTEXT.md:317). The ERDDAP value-added products carry `GEO_U` and `GEO_V` (geostrophic, cm/s) to 2019-03-30 (item 9). The Argo analyses themselves carry T and S only. Nothing from INCOIS carries w.

### 16. About 4,000 Argo floats - HOLDS

"Today, even with close to 4000 active floats..." https://argo.ucsd.edu/about/status/

### 17. The float cycle - PARTLY

"Each sinks to two kilometres, drifts for ten days and rises measuring on the way up." (explore.ts:197-198)

https://argo.ucsd.edu/about/ : it "stabilizes at a pre-set level, usually 1 km", and after ten days it "first descend[s] to 2km and then return[s] to the surface measuring". Floats drift at 1 km, not 2 km.

### 18. SARAT - HOLDS

https://sarat.incois.gov.in/sarat/home.jsp : "Search And Rescue Aid Tool (SARAT) for facilitating the search and rescue operations in the seas"; "The movement of the missing objects are governed mainly by the currents and winds"; up to 60 object types. Waves are not named on that page; the sentence in explore.ts is a general statement and still reads true.

### 19. Two seas - HOLDS

The 3.0 kg/m3 and 3.7 PSU are **build figures** (explore.ts:175-181 names the boxes), not literature claims. The magnitude agrees with the literature: "west of 75 E and north of 15 N ... exceeding 36", "east of 80 E and north of 15 N ... can be lower than 30". https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1610528/full . At about 0.77 kg/m3 per PSU, 3.7 PSU gives roughly 2.8 kg/m3, which fits 3.0.

### 20. 60 kJ/cm2 - PARTLY

"Above 60 kJ/cm² is the usual threshold for rapid intensification." (guide.ts:211, 373; index.html:826 "Above 60 kJ/cm2 ..."; README-full.md:75)

Mainelli, DeMaria, Shay and Goni 2008, Weather and Forecasting 23, 3-16 (https://www.aoml.noaa.gov/phod/people/goni/papers/Mainellietal.pdf): OHC "becomes a statistically significant predictor for all values of the threshold above 50 kJ cm-2 with an optimal value of 60"; "For values above 60 kJ cm-2, the OHC adds a positive correction to the TC intensity forecast"; and "the 60 kJ cm-2 threshold in SHIPS is not a requirement for a category 5 storm." So 60 is an empirical threshold from NHC's SHIPS model in the Atlantic, where heat potential starts to add intensity. It is not a rapid-intensification threshold as such, and it is not Leipper and Volgenau's (they give about 16 kJ cm-2 per day to sustain a storm, per the same paper). Shay, Goni and Black 2000 not fetched.

### 21. TCHP definition - HOLDS

Leipper and Volgenau 1972, "Hurricane Heat Potential of the Gulf of Mexico", J. Phys. Oceanogr. 2, 218-224 (https://ui.adsabs.harvard.edu/abs/1972JPO.....2..218L/abstract). Mainelli et al. 2008: "The sea surface temperature excess above 26 C is then integrated from the depth of that isotherm to the surface to give the OHC."

### 22. 26 degC floor - HOLDS

Gray 1968, Monthly Weather Review 96, 669-700 (https://mountainscholar.org/bitstreams/a90e00eb-8d3b-4145-9e36-b9cb4e0eabdf/download). Its climatological requirements list ocean temperature above about 26 degC. The PDF is a scan and the text layer is noisy, so the exact figure (26 or 26.5) could not be read cleanly.

### 23. de Boyer Montegut et al. 2004 - HOLDS

SEANOE dataset for the climatology: "threshold value for the density of 0.03kg/m3", "surface reference depth fixed at 10m", citing de Boyer Montegut et al. 2004, JGR 109, C12003, doi:10.1029/2004JC002378. https://www.seanoe.org/data/00806/91774/ . The paper's abstract (403 today at Wiley) gives dT = 0.2 degC or d sigma-theta = 0.03 kg/m3 from 10 m. The code uses sigma-theta (pipeline/oceanverity/hazard.py:55), which matches.

### 24. World Ocean Atlas 2023 - HOLDS

- https://www.ncei.noaa.gov/products/world-ocean-atlas : 1991-2020 climate normals; 1-degree and 0.25-degree; annual, seasonal and monthly.
- NOAA Atlas NESDIS 89, WOA23 Vol. 1 Temperature: "annual and seasonal at 102 standard depths from surface to 5500 m, and monthly at 57 standard depths from surface to 1500 m." https://repository.library.noaa.gov/view/noaa/60599/noaa_60599_DS1.pdf
- NCEI THREDDS OPeNDAP timed out at 60 s today; the HTTPS file server returned 503.

### 25. Cyclone Montha - HOLDS

IMD RSMC New Delhi, Best Tracks Data 1982-2026, sheet 2025 (https://rsmcnewdelhi.imd.gov.in/download.php?path=uploads/best-track/78b4b0_Best_Tracks__Data__1982-2026_.xlsx):
- D at 0000 UTC 25-10-2025, 10.8 N 89.0 E, 20 kt; DD 26 Oct; CS 1800 UTC 26 Oct.
- SCS from 0000 UTC 28-10-2025; peak 50 kt, 990 hPa.
- "Crossed Andhra Pradesh and Yanam between Machilipatnam and Kalingapatnam to the south of Kakinada close to Narsapur near latitude 16.35N and longitude 81.70 E during 1800 UTC-1900 UTC of 28."
- 30-10-2025 0000 UTC: "Weakened into a Well Marked Low Pressure Area".

Also IMD advisory 16, 1500 UTC 28-10-2025. https://rsmcnewdelhi.imd.gov.in/uploads/archive/2/2_063b93_16._Tropical_Cyclone_Advisory_No._16_based_on_1500_UTC_of_28.10.2025.pdf

### 26. PS 26067 text - HOLDS

https://www.sih.gov.in/sih2026PS (reachable today): PS 26067, Category **Software**, Theme **Disaster Management**. Dataset links: "a. Numerical Ocean Model Outputs: https://las.incois.gov.in/ & https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description b. Argo Global Data: ftp://ftp.ifremer.fr/ifremer/argo c. Glider Data: ftp://ftp.ifremer.fr/ifremer/glider/v2/". It names "HF-radar, Acoustic Doppler Current Profiler (ADCP)", "machine-learning derived products" and "OGC WMS/WCS".

### 27. NOAA OSMC - HOLDS

https://erddap.aoml.noaa.gov/gdp/erddap/info/OSMC_RealTime/index.csv : title "OSMC flattened observations from GTS"; licence CC0 1.0.

### 28. Ifremer Argo ERDDAP - HOLDS

https://erddap.ifremer.fr/erddap/info/ArgoFloats/index.csv : "Argo Float Measurements", live.

### 29. RAMA - PARTLY

"Three are RAMA, the joint MoES-NOAA array." (guide.ts:879)

NOAA PMEL: "The first RAMA buoys were deployed by NOAA PMEL in 2004"; "MoES has extended operational support to the RAMA array since the earliest deployments"; NOAA and MoES renewed the agreement on 2021-08-09. https://www.pmel.noaa.gov/gtmba/news-story/noaa-renews-decade-long-partnership-ministry-earth-sciences-india-and-launches-new-joint . Partners also "include Indonesia, China, the USA, and the Bay of Bengal Large Marine Ecosystem (BOBLME) program". https://www.pmel.noaa.gov/gtmba/pmel-theme/indian-ocean-rama . It is NOAA's array with MoES as one partner, not a two-party joint array.

### 30. OMNI - HOLDS

Same PMEL page: OMNI "initially deployed in 2012", operated by NIOT; the joint RAMA-OMNI data portal is hosted at incois.gov.in (https://incois.gov.in/site/datainfo/jointportal.jsp).

### 31. SIH deadline - WRONG

"**20 September 2026** on the PS page as mirrored by community sites." (ppt/PLAN.md:24); "treat 20 September 2026 as the operative PS deadline" (ppt/NOTES.md:216)

https://www.sih.gov.in/sih2026PS row for PS 26067: `<td>SIH26067</td> <td>4/500</td> <td>Disaster Management</td> <td>30 September 2026</td>`. The home page carries "Deadline for Idea Submission has been Extended". The mirror (https://sih-2026-explorer-pearl.vercel.app/problems/SIH26067/) still shows 20 September and the old theme, Smart Automation.

---

## Could not verify

- **VAM input data** (8b): no method document found; ERDDAP metadata is silent.
- **INCOIS LAS time axes**, including `Godas 2025` ending 2025-05-22: OPeNDAP returned nothing within 120-240 s.
- **A login** on INCOIS HF radar/ADCP: the host is unreachable; only the request-form policy is sourced.
- **Copernicus interim (myint) end date**: no separate dataset in the STAC listing.
- **CPC Godas**, **Shay, Goni and Black 2000**, and the **full de Boyer Montegut 2004 text** (Wiley 403): not fetched.
- **Gray 1968 exact threshold**: scanned PDF, noisy text.
- Not tried, per instruction: tds.hycom.org, coastwatch.pfeg.noaa.gov.

## Noticed in passing (internal, not counted)

- guide.ts:931-932 (and README-full.md:255) says density is worked out "at each cell's own pressure", but
  pipeline/oceanverity/density.py:16 and :89 compute `gsw.sigma0`, potential density referenced to the
  surface. Suggested: "worked out here with TEOS-10 from INCOIS's temperature and salinity analyses
  for %d, as potential density referenced to the surface".

## Wording fixes to apply

| file:line | Current text | Replacement | Why |
| --- | --- | --- | --- |
| web/requirements.html:584-585 | No maintained pure-Python server, and OPeNDAP is what this community actually uses. It is already served. | No pure-Python WCS server fits this API: THREDDS is Java and EOxServer runs on MapServer. The same numbers are already served over OPeNDAP, as INCOIS's ERDDAP and NOAA's THREDDS serve theirs. | Copernicus dropped OPeNDAP in 2024; pure-Python OGC API - Coverages (pygeoapi) exists |
| CONTEXT.md:307-308 | WCS stays out: no maintained pure-Python server, and the numbers are already on OPeNDAP, which is what this community actually uses. | WCS stays out: no pure-Python WCS server fits (THREDDS is Java, EOxServer needs MapServer; pygeoapi offers only its successor, OGC API - Coverages), and the numbers are already on OPeNDAP. | Same |
| docs/README-full.md:673-674 | There is no maintained pure-Python WCS server, and the numbers are already on OPeNDAP, which is what this community actually uses. | No pure-Python WCS server fits this API, and the numbers are already on OPeNDAP. | Same |
| web/requirements.html:591-592 | India's are behind a login at `services.incois.gov.in`, which does not resolve. A data-policy fact. | India's are not open: INCOIS serves in-situ data on a request form and restricts data inside the EEZ, and `services.incois.gov.in` resolves only to a private address. A data-policy fact. | Resolves to 172.16.1.134; login unconfirmed |
| web/requirements.html:595-596 | Ends 2025-05-22, under three months before the window opens. | INCOIS's LAS copy ends 2025-05-22, under three months before the window opens, and its OPeNDAP does not answer. NOAA's own Godas runs to July 2026, as monthly means only. | NOAA PSL Godas has Jan-Jul 2026 |
| CONTEXT.md:316-317 | that needs a vertical velocity `w`, Copernicus publish `uo` and `vo` and no `w`, and INCOIS publish neither | that needs a vertical velocity `w`, which only a model supplies - Copernicus publish a modelled `wo` that nobody measured, and INCOIS's analysis carries no currents at all | `wo` is in 001_024; INCOIS ERDDAP had geostrophic U/V to 2019 |
| docs/adr/0017-flow-as-moving-dots.md:13-14 | The Copernicus product this platform reads publishes `uo` and `vo` and no `w`, and INCOIS's own analysis publishes neither. | The Copernicus dataset this platform reads carries only `uo` and `vo`; the same product does publish a modelled `wo`, which no instrument measured, and INCOIS's own analysis publishes no currents. | Same |
| README.md:353 | Nobody publishes vertical velocity for this region, so a 3-D particle would claim a motion no one measured. | Vertical velocity exists here only as model output (Copernicus `wo`), never measured, so a 3-D particle would claim a motion no one measured. | Same |
| docs/README-full.md:677-678 | it needs a vertical velocity and neither provider publishes one | it needs a vertical velocity, which exists only as a model output nobody measured | Same |
| ppt/DECK.md:543 | neither provider publishes a vertical velocity | vertical velocity exists only as a model output nobody measured | Same |
| web/src/explore.ts:197-198 | Each sinks to two kilometres, drifts for ten days and rises measuring on the way up. | Each drifts for ten days a kilometre down, sinks to two, and rises measuring on the way up. | Argo parks at 1 km |
| web/src/guide.ts:211 and :373 | Above 60 kJ/cm² is the usual threshold for rapid intensification. | Above about 60 kJ/cm², heat potential starts adding strength in NOAA's hurricane forecast model. | Mainelli et al. 2008: SHIPS threshold, "not a requirement" |
| web/index.html:826 | Above 60 kJ/cm2 is the usual threshold for rapid intensification | Above about 60 kJ/cm2, heat potential starts adding strength in NOAA's hurricane forecast model (Mainelli et al. 2008) | Same |
| docs/README-full.md:75 | Above 60 kJ/cm² is the usual threshold for rapid intensification. | Above about 60 kJ/cm², heat potential starts adding strength in NOAA's hurricane forecast model (Mainelli et al. 2008). | Same |
| web/src/guide.ts:879 | Three are RAMA, the joint MoES-NOAA array. | Three are RAMA, NOAA's Indian Ocean array, run with India's MoES among its partners. | PMEL lists several partners |
| ppt/PLAN.md:24 | 20 September 2026 on the PS page as mirrored by community sites. Not checked on sih.gov.in itself - check the portal. | 30 September 2026, read on sih.gov.in/sih2026PS on 2026-09-14 (the portal says the deadline was extended; community mirrors still show 20 September). | Primary source |
| ppt/NOTES.md:216 | treat 20 September 2026 as the operative PS deadline until you confirm otherwise on the portal | the portal shows 30 September 2026 for SIH26067 (checked 2026-09-14) | Primary source |
| docs/NUMBERS.md:35 | Copernicus reanalysis "ends in 2022" | Resolve: STAC shows 1993-01-01 to 2026-06-23 on 2026-09-14 | Primary source |
