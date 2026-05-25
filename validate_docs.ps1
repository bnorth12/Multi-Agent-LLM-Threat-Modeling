$base="data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment"
$fc=Import-Csv "$base/function_catalog.csv"
$ig=Import-Csv "$base/interface_governance_matrix.csv"

# 1) Function catalog decomposition consistency
$allocIssues = New-Object System.Collections.Generic.List[object]
foreach($f in $fc){
  $fid=$f.function_id
  $parts=$fid -split "\."
  if($parts.Count -ne 3){
    $allocIssues.Add([pscustomobject]@{type="function_id_format";function_id=$fid;detail="Expected AAA.BBBB.NNN"}) | Out-Null
    continue
  }
  $l0Code=$parts[0]; $l1CodeFromId=$parts[1]; $index=$parts[2]
  $expectedL0 = switch($f.l0_domain){ "AVIATE" {"AVI"}; "NAVIGATE" {"NAV"}; "COMMUNICATE" {"COM"}; "OPERATE" {"OPS"}; default {""} }
  if($expectedL0 -and $l0Code -ne $expectedL0){ $allocIssues.Add([pscustomobject]@{type="l0_mismatch";function_id=$fid;detail="id_l0=$l0Code expected_l0=$expectedL0"}) | Out-Null }
  if($f.l1_code -and $l1CodeFromId -ne $f.l1_code){ $allocIssues.Add([pscustomobject]@{type="l1_code_mismatch";function_id=$fid;detail="id_l1=$l1CodeFromId csv_l1=$($f.l1_code)"}) | Out-Null }
  if($f.function_level -eq "L1" -and $index -ne "001"){ $allocIssues.Add([pscustomobject]@{type="l1_index_not_001";function_id=$fid;detail="index=$index"}) | Out-Null }
  if($f.function_level -eq "L2" -and $index -eq "001"){ $allocIssues.Add([pscustomobject]@{type="l2_index_001";function_id=$fid;detail="L2 index should not be 001"}) | Out-Null }
}

# 2) Interface endpoint existence + level extraction
$fcById=@{}; foreach($f in $fc){ $fcById[$f.function_id]=$f }
$edgeIssues = New-Object System.Collections.Generic.List[object]; $edgeClass = New-Object System.Collections.Generic.List[object]
foreach($e in $ig){
  $p=$e.producer_function_id; $c=$e.consumer_function_id
  $pf= if($fcById.ContainsKey($p)){$fcById[$p]}else{$null}; $cf= if($fcById.ContainsKey($c)){$fcById[$c]}else{$null}
  if(-not $pf){ $edgeIssues.Add([pscustomobject]@{type="missing_producer";interface_id=$e.interface_id;producer=$p;consumer=$c;detail="producer not in catalog"})|Out-Null; continue }
  if(-not $cf){ $edgeIssues.Add([pscustomobject]@{type="missing_consumer";interface_id=$e.interface_id;producer=$p;consumer=$c;detail="consumer not in catalog"})|Out-Null; continue }
  $sameL0 = ($pf.l0_domain -eq $cf.l0_domain); $sameL1 = ($pf.l1_code -eq $cf.l1_code); $pair = "$($pf.function_level)->$($cf.function_level)"
  $class = if($sameL0 -and $sameL1){"intra_l1"} elseif($sameL0 -and -not $sameL1){"intra_l0_cross_l1"} else {"cross_l0"}
  $edgeClass.Add([pscustomobject]@{interface_id=$e.interface_id;class=$class;pair=$pair;p=$p;c=$c;p_l0=$pf.l0_domain;c_l0=$cf.l0_domain;p_l1=$pf.l1_code;c_l1=$cf.l1_code})|Out-Null
  if($pair -eq "L2->L2" -and -not $sameL0){ $edgeIssues.Add([pscustomobject]@{type="cross_domain_l2_to_l2";interface_id=$e.interface_id;producer=$p;consumer=$c;detail="Cross-domain L2-to-L2"})|Out-Null }
  if($pair -eq "L1->L1" -and -not $sameL0){ $edgeIssues.Add([pscustomobject]@{type="cross_domain_l1_to_l1";interface_id=$e.interface_id;producer=$p;consumer=$c;detail="Cross-domain L1-to-L1"})|Out-Null }
}

# 3) Data-flow decomposition similarity score
$totalEdges=$edgeClass.Count; $intraL1=@($edgeClass|?{$_.class -eq "intra_l1"}).Count; $intraL0=@($edgeClass|?{$_.class -eq "intra_l0_cross_l1"}).Count; $crossL0=@($edgeClass|?{$_.class -eq "cross_l0"}).Count

# 4) Summaries
Write-Output "FUNCTION_COUNT=$($fc.Count)"; Write-Output "INTERFACE_COUNT=$($ig.Count)"
Write-Output "ALLOC_ISSUE_COUNT=$($allocIssues.Count)"; Write-Output "EDGE_ISSUE_COUNT=$($edgeIssues.Count)"
Write-Output "EDGE_CLASS_intra_l1=$intraL1"; Write-Output "EDGE_CLASS_intra_l0_cross_l1=$intraL0"; Write-Output "EDGE_CLASS_cross_l0=$crossL0"
if($totalEdges -gt 0){ Write-Output "DECOMPOSITION_SIMILARITY_PERCENT=$([math]::Round((($intraL1 + $intraL0) / $totalEdges) * 100,2))" }

# 5) Print violation details
Write-Output "ALLOC_ISSUES_START"; $allocIssues | Select -First 25 | ConvertTo-Csv -NoTypeInformation | Select -Skip 1; Write-Output "ALLOC_ISSUES_END"
Write-Output "EDGE_ISSUES_START"; $edgeIssues | Select -First 25 | ConvertTo-Csv -NoTypeInformation | Select -Skip 1; Write-Output "EDGE_ISSUES_END"
Write-Output "CROSS_L0_EDGES_START"; $edgeClass | ?{$_.class -eq "cross_l0"} | Select -First 20 interface_id,pair,p,c,p_l0,c_l0 | ConvertTo-Csv -NoTypeInformation | Select -Skip 1; Write-Output "CROSS_L0_EDGES_END"
