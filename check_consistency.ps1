$paths = @{
    fmea = "data/inputs/Aerospace_Architecture/05_safety_analysis/fmea_hazard_register.csv"
    dec  = "data/inputs/Aerospace_Architecture/05_safety_analysis/fmea_hsa_subsystem_decomposition_matrix.csv"
    fc   = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/function_catalog.csv"
    ig   = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/interface_governance_matrix.csv"
    inf  = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/l3_l4_l5_inference_matrix.csv"
    gap  = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/l2_l1_rollup_gap_register.csv"
    cl   = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/control_loop_closure_matrix.csv"
    bc   = "data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/interface_boundary_classification_register.csv"
}

function Load-Csv($p) { if (Test-Path $p) { return Import-Csv $p } else { return @() } }

$dfmea = Load-Csv $paths.fmea
$ddec  = Load-Csv $paths.dec
$dfc   = Load-Csv $paths.fc
$dig   = Load-Csv $paths.ig
$dinf  = Load-Csv $paths.inf
$dgap  = Load-Csv $paths.gap
$dcl   = Load-Csv $paths.cl
$dbc   = Load-Csv $paths.bc

function Parse-Ranges($str) {
    if (-not $str) { return @() }
    $ids = @()
    $parts = $str -split '[,;]'
    foreach ($p in $parts) {
        $p = $p.Trim()
        if ($p -match '([A-Z]+)-(\d+)\.\.([A-Z]+)-(\d+)') {
            $prefix = $Matches[1]; $start = [int]$Matches[2]; $end = [int]$Matches[4]
            for ($i=$start; $i -le $end; $i++) { $ids += "$prefix-$($i.ToString('000'))" }
        } elseif ($p -match '([A-Z]+)-(\d+)') {
            $ids += $p
        }
    }
    return $ids | Select-Object -Unique
}

Write-Host "`n1) ROW COUNTS"
Write-Host "FMEA: $($dfmea.Count)"
Write-Host "DEC: $($ddec.Count)"
Write-Host "FC: $($dfc.Count)"
Write-Host "IG: $($dig.Count)"
Write-Host "INF: $($dinf.Count)"
Write-Host "GAP: $($dgap.Count)"
Write-Host "CL: $($dcl.Count)"
Write-Host "BC: $($dbc.Count)"

Write-Host "`n2) FM/HZ COVERAGE"
$coveredIds = $ddec | ForEach-Object { Parse-Ranges $_.fm_id_scope; Parse-Ranges $_.hz_id_scope } | Select-Object -Unique
$allFmHz = $dfmea.entry_id
$uncovered = $allFmHz | Where-Object { $_ -notin $coveredIds }
Write-Host "Uncovered count: $($uncovered.Count)"
if ($uncovered.Count -gt 0) { Write-Host "First 20: $($uncovered | select -First 20)" }

Write-Host "`n3) FUNCTION-FLOW CONSISTENCY"
$fcIds = $dfc.function_id
$igFuncs = ($dig.producer_function_id + $dig.consumer_function_id) | Where-Object { $_ } | Select-Object -Unique
$missingFc = $igFuncs | Where-Object { $_ -notin $fcIds }
Write-Host "Missing from Catalog: $($missingFc.Count)"
$unrefFc = $fcIds | Where-Object { $_ -notin $igFuncs }
Write-Host "Unreferenced in Interfaces count: $($unrefFc.Count)"
if ($unrefFc.Count -gt 0) { Write-Host "First 40: $($unrefFc | select -First 40)" }

Write-Host "`n4) HIERARCHY INTEGRITY"
$l1s = $dfc | Where-Object { $_.level -eq 'L1' }
Write-Host "L1 Row Count: $($l1s.Count)"
$l1WithNoL2 = $l1s.function_id | Where-Object { $id = $_; -not ($dfc | Where-Object { $_.parent_id -eq $id }) }
Write-Host "L1 with zero L2 children: $($l1WithNoL2.Count)"
$dfc | Group-Object domain | Select-Object Name, Count | ForEach-Object { Write-Host "Domain: $($_.Name) - Functions: $($_.Count)" }

Write-Host "`n5) BOTTOM-UP LINKAGE"
$infFmeaMissing = $dinf.entry_id | Where-Object { $_ -notin $dfmea.entry_id }
$infL2Missing = $dinf.l2_function_id | Where-Object { $_ -notin $fcIds }
$igIds = $dig.interface_id
$infIgMissing = $dinf.flow_interface_id | Where-Object { $_ -and ($_ -notin $igIds) }
Write-Host "Inference -> FMEA missing: $($infFmeaMissing.Count)"
Write-Host "Inference -> FC missing: $($infL2Missing.Count)"
Write-Host "Inference -> IG missing: $($infIgMissing.Count)"

Write-Host "`n6) CONTROL-LOOP & BOUNDARY"
$clIgMissing = $dcl.required_interface_ids -split '[,;]' | ForEach-Object {$_.Trim()} | Where-Object {$_ -and $_ -notin $igIds}
$clFcMissing = ($dcl.manager_func_id + $dcl.sensor_func_id + $dcl.controller_func_id + $dcl.effector_func_id) | Where-Object {$_ -and $_ -notin $fcIds}
$clHzMissing = $dcl.hazard_refs -split '[,;]' | ForEach-Object {$_.Trim()} | Where-Object {$_ -and $_ -notin $dfmea.entry_id}
Write-Host "CL -> IG missing: $($clIgMissing.Count)"
Write-Host "CL -> FC missing: $($clFcMissing.Count)"
Write-Host "CL -> FMEA missing: $($clHzMissing.Count)"
$bcIgMissing = $dbc.interface_id | Where-Object {$_ -notin $igIds}
$bcClMissing = $dbc.control_loop_id | Where-Object {$_ -and $_ -notin $dcl.control_loop_id}
Write-Host "Boundary -> IG missing: $($bcIgMissing.Count)"
Write-Host "Boundary -> CL missing: $($bcClMissing.Count)"

Write-Host "`n7) GAP REGISTER"
$gapFuncMissing = ($dgap.l1_id + $dgap.l2_id) | Where-Object {$_ -and $_ -notin $fcIds}
Write-Host "Gap -> FC missing: $($gapFuncMissing.Count)"
$dgap | Group-Object status | Select-Object Name, Count

Write-Host "`n8) TRACEABILITY SLICES (L0)"
$dfc | Group-Object domain | ForEach-Object {
    $domName = $_.Name; $ids = $_.Group.function_id
    $refCount = ($ids | Where-Object { $_ -in $igFuncs }).Count
    Write-Host "Domain: $domName - Total: $($ids.Count), Ref: $refCount, Unref: $($ids.Count - $refCount)"
}

Write-Host "`n9) OVERALL ORPHAN SUMMARY"
$orphans = [PSCustomObject] @{
    UncoveredFmHz = $uncovered.Count
    UnrefFunctions = $unrefFc.Count
    MissingFcRefs = ($missingFc.Count + $infL2Missing.Count + $clFcMissing.Count + $gapFuncMissing.Count)
    BrokenIgLinks = ($infIgMissing.Count + $clIgMissing.Count + $bcIgMissing.Count)
}
$orphans | Format-Table
