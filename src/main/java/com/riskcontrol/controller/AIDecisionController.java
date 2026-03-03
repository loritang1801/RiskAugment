package com.riskcontrol.controller;

import com.riskcontrol.dto.AIAnalysisDTO;
import com.riskcontrol.entity.AIDecisionRecord;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController
@RequestMapping("/api/ai-decisions")
@RequiredArgsConstructor
@Tag(name = "AI Decision Management", description = "APIs for AI decision records")
public class AIDecisionController {
    
    private final AIDecisionRecordRepository aiDecisionRecordRepository;
    
    @GetMapping("/case/{caseId}")
    @Operation(summary = "Get AI decision by case ID")
    public ResponseEntity<Map<String, Object>> getAIDecisionByCase(@PathVariable Long caseId) {
        log.info("Getting AI decision for case: {}", caseId);
        
        Optional<AIDecisionRecord> decision = aiDecisionRecordRepository.findTopByCaseIdAndDeletedAtIsNullOrderByCreatedAtDesc(caseId);
        
        Map<String, Object> response = new HashMap<>();
        
        if (decision.isPresent()) {
            response.put("status", "success");
            response.put("data", convertToDTO(decision.get()));
        } else {
            response.put("status", "success");
            response.put("data", null);
        }
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get AI decision by ID")
    public ResponseEntity<Map<String, Object>> getAIDecisionById(@PathVariable Long id) {
        log.info("Getting AI decision: {}", id);
        
        Optional<AIDecisionRecord> decision = aiDecisionRecordRepository.findById(id);
        
        Map<String, Object> response = new HashMap<>();
        
        if (decision.isPresent()) {
            response.put("status", "success");
            response.put("data", convertToDTO(decision.get()));
        } else {
            response.put("status", "error");
            response.put("message", "AI decision not found");
        }
        
        return ResponseEntity.ok(response);
    }
    
    private Map<String, Object> convertToDTO(AIDecisionRecord record) {
        Map<String, Object> dto = new HashMap<>();
        dto.put("id", record.getId());
        dto.put("caseId", record.getCaseId());
        dto.put("riskLevel", record.getRiskLevel());
        dto.put("confidenceScore", record.getConfidenceScore());
        dto.put("suggestedAction", record.getSuggestedAction());
        dto.put("keyRiskPoints", record.getKeyRiskPoints());
        dto.put("reasoning", record.getReasoning());
        dto.put("similarCasesAnalysis", record.getSimilarCasesAnalysis());
        dto.put("similarCasesDetails", record.getSimilarCasesDetails());
        dto.put("ruleEngineAlignment", record.getRuleEngineAlignment());
        dto.put("promptVersion", record.getPromptVersion());
        dto.put("totalTimeMs", record.getTotalTimeMs());
        dto.put("analysisSource", record.getAnalysisSource());
        dto.put("analysisModel", record.getAnalysisModel());
        dto.put("createdAt", record.getCreatedAt());
        return dto;
    }
}
