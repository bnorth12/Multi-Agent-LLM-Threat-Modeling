# FMEA and Hazard Safety Analysis Baseline

## Purpose

Provide a seeded, source-backed baseline of aerospace-relevant failure modes and hazards prior to functional-decomposition gap comparison.

## Method Framing

- FMEA lens: component or function failure mode -> local effect -> aircraft-level effect -> detectability and controls.
- Hazard lens: operational hazard condition -> severity context -> known contributors -> high-level mitigations.
- Evidence lens: each entry must reference a public source from `public_source_index.md`.

## Seeded Failure Modes (FMEA-Oriented)

| failure_mode_id | failure_mode | typical local effect | aircraft-level effect | source_ids |
| --- | --- | --- | --- | --- |
| FM-001 | Loss of thrust command authority | thrust mismatch or unavailable commanded thrust | inability to maintain required trajectory/performance margins | SRC-FAA-AC-1309, SRC-MIL-1629A |
| FM-002 | Uncommanded control-surface deflection | abnormal attitude/rate response | degraded controllability and potential LOC-I | SRC-FAA-AC-1309, SRC-SKY-LOCI |
| FM-003 | Erroneous air data input | incorrect speed/altitude/attitude references | wrong guidance or envelope-protection behavior | SRC-FAA-AC-1309, SRC-NASA-ASRS |
| FM-004 | Navigation sensor spoofing or jamming | invalid position/velocity estimate | route/guidance divergence and separation hazards | SRC-NASA-ASRS, SRC-ICAO-ADREP |
| FM-005 | Electrical bus loss or unstable distribution | power interruption to avionics/actuation chains | loss/degradation of critical systems and mode reversion | SRC-EASA-CS25, SRC-FAA-AC-1309 |
| FM-006 | Hydraulic pressure degradation | reduced actuator authority/response | degraded maneuver capability and handling qualities | SRC-EASA-CS25, SRC-MIL-1629A |
| FM-007 | Cabin pressure-control failure | pressure not maintained to target profile | crew/passenger physiological risk and diversion | SRC-EASA-CS25, SRC-NASA-ASRS |
| FM-008 | Datalink message corruption or replay | invalid command/constraint message accepted | intent mismatch between aircraft and external actors | SRC-FAA-CAST, SRC-ICAO-ADREP |
| FM-009 | Mission-sensor calibration drift | reduced sensor truth quality | incorrect fusion products and mission-tasking errors | SRC-NASA-ASRS, SRC-MIL-1629A |
| FM-010 | Domain isolation control failure | unauthorized cross-domain traffic | lateral movement risk and contamination of trusted domains | SRC-FAA-AC-1309, SRC-EASA-CS25 |
| FM-011 | Brake or anti-skid control degradation | reduced braking command quality or ineffective anti-skid behavior | runway overrun/excursion risk during landing or rejected takeoff | SRC-FAA-RWYSAFE, SRC-EASA-CS25 |
| FM-012 | Windshear detection or alerting failure | late/invalid warning to flight crew and automation | unstable energy state and loss-of-control proximity during critical phases | SRC-SKY-WINDSHEAR, SRC-FAA-CAST |
| FM-013 | Traffic surveillance track corruption/latency | stale or incorrect traffic picture in surveillance and coordination functions | reduced separation assurance and conflict-resolution delay | SRC-ICAO-ADREP, SRC-FAA-CAST |
| FM-014 | Loss of ability to change active radio frequency | crew cannot retune to assigned ATC or advisory channel | handoff failure, delayed clearances, and increased traffic-conflict risk | SRC-FAA-AIM-C4S2, SRC-ICAO-ADREP |
| FM-015 | Loss of ability to change radio mode | inability to select required communication mode (for example COM channel/radio state) | reduced communication continuity across flight phases and facilities | SRC-FAA-AIM-C4S2, SRC-NASA-ASRS |
| FM-016 | Loss of ability to set transponder code | assigned squawk cannot be entered or updated | surveillance identity ambiguity and degraded ATC conflict management | SRC-FAA-AIM-C4S1, SRC-ICAO-ADREP |
| FM-017 | Loss of ability to control altitude reporting/transponder state | inability to select required transponder/ADS-B operational state | degraded surveillance quality and reduced safety-alert effectiveness | SRC-FAA-AIM-C4S1, SRC-FAA-CAST |
| FM-018 | Stuck microphone continuous transmission | one transmitter blocks shared frequency | frequency blockage, missed clearances, and emergency-call masking | SRC-FAA-AIM-C4S2, SRC-NASA-ASRS |
| FM-019 | Incorrect radio frequency selection or cross-tuned operation | crew transmits/monitors wrong channel | communication with unintended station and traffic desynchronization | SRC-FAA-AIM-C4S2, SRC-ICAO-ADREP |
| FM-020 | Ground HF transmission exposure control failure | personnel access not controlled near active HF antenna on ground | RF contact burns and personnel injury risk | SRC-FCC-RFSAFE, SRC-OSHA-RFMW |
| FM-021 | Flight-director/autopilot mode-state inconsistency | displayed mode state differs from active control behavior | incorrect crew response and unstable path control | SRC-FAA-AC-1309, SRC-NASA-ASRS |
| FM-022 | Manual override path unavailable during automation anomaly | crew cannot promptly disengage or supersede faulty automation | delayed recovery and elevated LOC-I risk | SRC-FAA-AC-1309, SRC-EASA-CS25 |
| FM-023 | Route/procedure database integrity corruption | route constraints or leg definitions are invalid or stale | unsafe route execution or controlled-airspace deviation | SRC-FAA-CAST, SRC-ICAO-ADREP |
| FM-024 | Terrain awareness/alerting functional degradation | terrain conflict cues are absent, delayed, or incorrect | reduced terrain-separation margin and CFIT exposure | SRC-SKY-CFIT, SRC-NTSB-CAROL |
| FM-025 | Fuel quantity computation or transfer logic failure | fuel state estimate diverges from actual usable fuel | late diversion decisions and thrust-loss exposure | SRC-NTSB-CAROL, SRC-NASA-ASRS |
| FM-026 | Brake energy or temperature monitoring failure | high-energy braking condition is not correctly detected | brake damage progression and stopping-performance shortfall | SRC-FAA-RWYSAFE, SRC-EASA-CS25 |
| FM-027 | Ice-protection actuation failure | anti-ice/de-ice function does not engage or sustain | aerodynamic degradation and controllability reduction | SRC-FAA-CAST, SRC-SKY-LOCI |
| FM-028 | Smoke/fire detection false negative in occupied compartments | fire/smoke condition is not annunciated in time | delayed crew intervention and cabin/systems hazard escalation | SRC-EASA-CS25, SRC-NTSB-CAROL |
| FM-029 | Mission-priority arbitration deadlock | competing mission/safety requests are unresolved or unstable | unsafe command prioritization and flight-task interference | SRC-MIL-1629A, SRC-FAA-AC-1309 |
| FM-030 | Sensor-fusion confidence misclassification | fused tracks are over-trusted despite low source quality | incorrect decision support and tactical/operational error | SRC-NASA-ASRS, SRC-ICAO-ADREP |
| FM-031 | Flight-mode reversion annunciation loss | automatic mode downgrade occurs without timely or unambiguous annunciation | crew executes against wrong control-law assumptions | SRC-FAA-AC-1309, SRC-NASA-ASRS |
| FM-032 | Lateral and vertical guidance channel split-brain | displayed guidance mode indicates coupled state while channels are decoupled | path tracking divergence and unstable energy-path control | SRC-FAA-AC-1309, SRC-SKY-LOCI |
| FM-033 | Autopilot engagement with stale trim baseline | automation engages using stale trim or bias estimate | immediate pitch or roll transient and workload spike | SRC-EASA-CS25, SRC-NASA-ASRS |
| FM-034 | Envelope protection threshold mis-scheduling | protection limits are mapped to wrong flight-phase schedule | late or incorrect intervention near envelope boundaries | SRC-FAA-AC-1309, SRC-EASA-CS25 |
| FM-035 | Control-law gain-set corruption after phase transition | gain table switches to an invalid set during mode transition | pilot-induced oscillation susceptibility and handling-quality degradation | SRC-FAA-AC-1309, SRC-SKY-LOCI |
| FM-036 | Servo runaway detection timeout | runaway actuator detection does not trigger within required window | escalating attitude excursion before crew recovery action | SRC-EASA-CS25, SRC-FAA-AC-1309 |
| FM-037 | RNAV leg sequencing failure | waypoint transition logic advances late, early, or to wrong leg | track divergence from cleared procedure | SRC-ICAO-ADREP, SRC-FAA-CAST |
| FM-038 | Constraint-evaluation logic omission | published altitude or speed constraints are not enforced in path computation | clearance non-compliance and separation margin reduction | SRC-FAA-CAST, SRC-ICAO-ADREP |
| FM-039 | Navigation integrity alert suppression | RAIM or equivalent integrity alert is not propagated to crew systems | invalid position solution used for tactical navigation | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| FM-040 | Hold and procedure-turn geometry computation error | turn radius or timing model is computed from incorrect wind or speed assumptions | protected airspace boundary exceedance | SRC-FAA-CAST, SRC-ICAO-ADREP |
| FM-041 | Navigation timebase desynchronization | sensor fusion and procedure timing use inconsistent clocks | sequence and prediction errors across route legs | SRC-NASA-ASRS, SRC-ICAO-ADREP |
| FM-042 | Baro-VNAV reference mismatch | vertical guidance references wrong barometric setting source | unstable vertical path and altitude bust risk | SRC-FAA-CAST, SRC-NASA-ASRS |
| FM-043 | Receiver squelch stuck-closed | valid incoming transmissions are suppressed by receiver gating | missed clearances and delayed conflict response | SRC-FAA-AIM-C4S2, SRC-NASA-ASRS |
| FM-044 | Receiver squelch stuck-open | persistent noise masks valid communication content | message comprehension failures and crew overload | SRC-FAA-AIM-C4S2, SRC-NASA-ASRS |
| FM-045 | Transponder panel to transmitter state desynchronization | displayed code or mode does not match emitted surveillance state | controller sees incorrect aircraft identity or status | SRC-FAA-AIM-C4S1, SRC-ICAO-ADREP |
| FM-046 | ADS-B validity flag stuck valid | invalid position or velocity data remains flagged as valid for broadcast | false traffic picture and alerting degradation | SRC-FAA-AIM-C4S1, SRC-FAA-CAST |
| FM-047 | Voice and data clearance channel divergence | CPDLC or datalink clearance state diverges from active voice clearance | conflicting execution of route or altitude instructions | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| FM-048 | Guard frequency monitoring unavailable | emergency guard monitoring function is disabled or ineffective | delayed awareness of emergency traffic and priority coordination | SRC-FAA-AIM-C4S2, SRC-ICAO-ADREP |

## Seeded Hazard Conditions (Operational Safety-Oriented)

| hazard_id | hazard_condition | representative consequence | source_ids |
| --- | --- | --- | --- |
| HZ-001 | Loss of Control In-Flight (LOC-I) | catastrophic control loss risk | SRC-SKY-LOCI, SRC-FAA-CAST |
| HZ-002 | Controlled Flight Into Terrain (CFIT) | terrain collision without loss of aircraft control | SRC-SKY-CFIT, SRC-ICAO-ADREP |
| HZ-003 | Runway Excursion | aircraft departs runway surface during takeoff/landing | SRC-SKY-RE, SRC-FAA-CAST |
| HZ-004 | Midair collision/loss of separation | collision or near-collision due to awareness/coordination failure | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| HZ-005 | Fire or smoke event | crew workload saturation and potential loss of essential capability | SRC-EASA-CS25, SRC-NTSB-CAROL |
| HZ-006 | Fuel starvation/fuel mismanagement | engine flameout or thrust shortfall | SRC-NTSB-CAROL, SRC-NASA-ASRS |
| HZ-007 | Icing-induced performance degradation | lift/drag and controllability deterioration | SRC-FAA-CAST, SRC-NASA-ASRS |
| HZ-008 | Depressurization event | physiological hazard and emergency descent/diversion | SRC-EASA-CS25, SRC-NTSB-CAROL |
| HZ-009 | Communication breakdown with ATC/operations | desynchronized intent and reduced separation assurance | SRC-ICAO-ADREP, SRC-FAA-CAST |
| HZ-010 | Hazardous mission-system to flight-system interaction | conflict between mission priorities and safe-flight constraints | SRC-FAA-AC-1309, SRC-MIL-1629A |
| HZ-011 | Runway incursion | conflicting occupancy of runway by aircraft/vehicle/person with collision or high-energy avoidance maneuver risk | SRC-SKY-RWYINC, SRC-FAA-RWYSAFE |
| HZ-012 | Windshear encounter | abrupt wind vector change in departure/approach corridor with unstable flight path and recovery workload escalation | SRC-SKY-WINDSHEAR, SRC-FAA-CAST |
| HZ-013 | Wildlife strike | wildlife impact to airframe/engine/windscreen with damage, thrust degradation, and potential emergency diversion | SRC-FAA-WILDLIFE, SRC-SKY-BIRD |
| HZ-014 | ATC handoff breakdown due communication-control failure | inability to establish contact with next controlling facility and delayed conflict resolution actions | SRC-FAA-AIM-C4S2, SRC-ICAO-ADREP |
| HZ-015 | Surveillance identity ambiguity from transponder-code management failure | incorrect or missing code assignment in shared airspace; tracking confusion and reduced separation assurance | SRC-FAA-AIM-C4S1, SRC-ICAO-ADREP |
| HZ-016 | False emergency or distress surveillance state | inadvertent emergency-code behavior and alert triggering; unnecessary emergency response and controller workload surge | SRC-FAA-AIM-C4S1, SRC-FAA-CAST |
| HZ-017 | Frequency blockage from stuck transmission | communication channel unavailable for routine or urgent traffic; missed instructions, delayed hazard response, and safety-margin erosion | SRC-FAA-AIM-C4S2, SRC-NASA-ASRS |
| HZ-018 | Ground personnel RF burn hazard near transmitting antenna | human exposure to active RF field near aircraft antenna during transmission; localized burn/injury and ground-operation interruption | SRC-FCC-RFSAFE, SRC-OSHA-RFMW |
| HZ-019 | Controlled-airspace deviation from route/procedure integrity failure | aircraft path diverges from cleared/expected route due integrity faults; separation risk and regulatory non-compliance exposure | SRC-ICAO-ADREP, SRC-FAA-CAST |
| HZ-020 | Unstable approach from automation mode confusion | crew/automation mismatch during approach energy-path control; go-around overload, runway excursion, or LOC-I precursor | SRC-SKY-LOCI, SRC-FAA-CAST |
| HZ-021 | Terrain-separation loss from terrain-alert degradation | terrain hazard not recognized in time for corrective action; elevated CFIT probability | SRC-SKY-CFIT, SRC-NTSB-CAROL |
| HZ-022 | Rejected-takeoff or landing overrun due braking-function degradation | stopping capability reduced during high-energy phase; runway overrun/excursion and structural damage risk | SRC-FAA-RWYSAFE, SRC-SKY-RE |
| HZ-023 | Icing-driven controllability hazard from anti-ice functional failure | critical surfaces/inputs degraded by icing accumulation; significant performance and control-margin loss | SRC-FAA-CAST, SRC-SKY-LOCI |
| HZ-024 | Cabin smoke/fire incapacitation escalation | delayed detection or containment causes crew/passenger impairment; emergency descent/diversion and potential loss of essential function | SRC-EASA-CS25, SRC-NTSB-CAROL |
| HZ-025 | Mission-to-flight authority conflict hazard | mission priorities interfere with safe-flight authority chain; unsafe maneuvering decisions and command conflict | SRC-FAA-AC-1309, SRC-MIL-1629A |
| HZ-026 | Dispatch with latent critical fault due health-monitoring misclassification | degraded system dispatched under false-normal status; in-flight failure manifestation under load/stress | SRC-NTSB-CAROL, SRC-NASA-ASRS |
| HZ-027 | Automation surprise during critical phase | unannounced or misunderstood control-mode transition occurs in high-workload segment; loss of stabilised path criteria and LOC-I precursor | SRC-FAA-AC-1309, SRC-SKY-LOCI |
| HZ-028 | Guidance-law mismatch hazard | displayed and active guidance laws diverge during coupled operations; incorrect pilot intervention timing and path destabilization | SRC-FAA-AC-1309, SRC-NASA-ASRS |
| HZ-029 | Runaway control excursion before detection | actuator runaway grows beyond recoverable margins prior to alert; severe attitude upset and high structural load exposure | SRC-EASA-CS25, SRC-FAA-AC-1309 |
| HZ-030 | Procedure containment loss in terminal airspace | navigation computation fault drives aircraft outside protected procedure volume; terrain and traffic conflict exposure | SRC-ICAO-ADREP, SRC-FAA-CAST |
| HZ-031 | Altitude and speed restriction non-compliance hazard | constraint processing fault causes deviation from cleared profile; separation reduction and ATC intervention demand | SRC-FAA-CAST, SRC-ICAO-ADREP |
| HZ-032 | Invalid navigation integrity acceptance hazard | crew and automation continue with invalid position integrity state; controlled-airspace deviation and CFIT precursor conditions | SRC-ICAO-ADREP, SRC-SKY-CFIT |
| HZ-033 | Surveillance truth mismatch hazard | emitted surveillance identity or validity differs from cockpit indication; controller and crew operate on inconsistent traffic identity assumptions | SRC-FAA-AIM-C4S1, SRC-ICAO-ADREP |
| HZ-034 | Clearance channel divergence hazard | voice and datalink clearance states conflict without reconciliation; execution of contradictory clearances and conflict-risk increase | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| HZ-035 | Emergency channel awareness loss | guard monitoring failure prevents timely awareness of distress traffic; delayed emergency coordination and hazard response | SRC-FAA-AIM-C4S2, SRC-FAA-CAST |

## Tranche 2 Through Tranche 4 Representative Additions

The machine-readable register is the authoritative complete list for tranche execution depth. Representative examples from executed tranches are shown below.

### Tranche 05-11 Representative Failure Modes

| failure_mode_id | failure_mode | typical local effect | aircraft-level effect | source_ids |
| --- | --- | --- | --- | --- |
| FM-050 | Brake-by-wire command dropout | brake command path intermittently opens under vibration or load | inconsistent deceleration and longer stopping distance | SRC-FAA-RWYSAFE, SRC-EASA-CS25 |
| FM-062 | Ice detector false negative in mixed-phase precipitation | sensor fails to detect icing onset in mixed conditions | delayed anti-ice response and contamination growth | SRC-SKY-WINDSHEAR, SRC-FAA-CAST |
| FM-071 | Geofence enforcement bypass during replanning | route replanner applies path update without boundary guard checks | unauthorized entry into restricted volume | SRC-ICAO-ADREP, SRC-FAA-CAST |
| FM-089 | Battery state-of-charge estimator drift | estimator overstates available reserve energy | emergency endurance shorter than expected | SRC-EASA-CS25, SRC-NASA-ASRS |
| FM-101 | Oxygen mask deployment inhibit not cleared | inhibit flag persists into active pressurization hazard state | delayed oxygen availability to occupants | SRC-EASA-CS25, SRC-NTSB-CAROL |
| FM-123 | Watchdog restart loop masks root-cause alert | repeated subsystem restarts clear or suppress persistent fault annunciation | latent hazard remains unaddressed | SRC-FAA-AC-1309, SRC-NASA-ASRS |

### Tranche 05-11 Representative Hazards

| hazard_id | hazard_condition | representative consequence | source_ids |
| --- | --- | --- | --- |
| HZ-038 | High-energy stop insufficient deceleration hazard | runway overrun and structural damage risk | SRC-FAA-RWYSAFE, SRC-SKY-RE |
| HZ-044 | Windshear escape execution-delay hazard | energy deficit and terrain conflict precursor | SRC-SKY-WINDSHEAR, SRC-FAA-CAST |
| HZ-050 | Unauthorized mission command acceptance hazard | unsafe maneuver or payload actuation | SRC-FAA-AC-1309, SRC-MIL-1629A |
| HZ-060 | Electrical fire initiation from undetected arc hazard | smoke or fire propagation in equipment bays | SRC-EASA-CS25, SRC-NTSB-CAROL |
| HZ-067 | Apron collision from guidance misclassification hazard | aircraft-to-vehicle or aircraft-to-structure collision risk | SRC-ICAO-ADREP, SRC-FAA-RWYSAFE |
| HZ-074 | Alert flooding and crew-channelization hazard | critical cue miss and delayed mitigation | SRC-FAA-AC-1309, SRC-NTSB-CAROL |

## Tranche 05 Through Tranche 11 Representative Additions

Representative entries from the executed tranche 05-11 expansion are listed below. The full authoritative set remains in `fmea_hazard_register.csv`.

### Representative Failure Modes

| failure_mode_id | failure_mode | typical local effect | aircraft-level effect | source_ids |
| --- | --- | --- | --- | --- |
| FM-133 | Crew-alert tone and visual cue desynchronization | aural and visual alert channels present inconsistent urgency timing | mis-prioritized crew response to abnormal condition | SRC-FAA-AC-1309, SRC-NASA-ASRS |
| FM-136 | Time-sensitive networking gate schedule drift | deterministic network gate times drift under oscillator offset | control and status message latency bound violation | SRC-FAA-AC-1309, SRC-MIL-1629A |
| FM-144 | Deferred defect accumulation threshold misapplied | deferred defect threshold uses outdated fleet policy mapping | unsafe dispatch with excessive latent degradations | SRC-EASA-CS25, SRC-NTSB-CAROL |
| FM-151 | Decision-support confidence calibration drift | model confidence remains high under out-of-distribution observations | unsafe recommendation accepted without challenge | SRC-NASA-ASRS, SRC-MIL-1629A |
| FM-160 | Language localization truncates critical procedural qualifier | localized text drops limiting condition in emergency action step | action executed outside safe applicability envelope | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| FM-164 | Release train merges conflicting safety mitigations | parallel branches introduce mutually incompatible mitigation logic | net safety effect degraded at integration | SRC-FAA-AC-1309, SRC-MIL-1629A |

### Representative Hazards

| hazard_id | hazard_condition | representative consequence | source_ids |
| --- | --- | --- | --- |
| HZ-081 | Crew-alerting salience inversion hazard | delayed response to time-critical failure | SRC-FAA-AC-1309, SRC-NTSB-CAROL |
| HZ-085 | Unauthorized trusted-endpoint persistence hazard | unsafe command pathway remains open | SRC-FAA-AC-1309, SRC-MIL-1629A |
| HZ-089 | Maintenance-record integrity hazard | incorrect dispatch decision basis | SRC-NTSB-CAROL, SRC-FAA-AC-1309 |
| HZ-093 | Over-trusted autonomy recommendation hazard | unsafe automation directive execution | SRC-NASA-ASRS, SRC-FAA-AC-1309 |
| HZ-098 | Localization-induced procedural misapplication hazard | incorrect intervention with secondary hazards | SRC-ICAO-ADREP, SRC-NASA-ASRS |
| HZ-101 | Mitigation-regression integration hazard | latent risk increase post-integration | SRC-FAA-AC-1309, SRC-MIL-1629A |

## Next-Step Rule

Do not infer decomposition gaps from this seed list yet. First confirm source applicability and baseline validity for the target aircraft program, then perform structured comparison to the current functional decomposition.
