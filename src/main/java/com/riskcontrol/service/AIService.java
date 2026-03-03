package com.riskcontrol.service;

import com.riskcontrol.client.AIClient;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.AIAnalysisDTO;
import com.riskcontrol.entity.AIDecisionRecord;
import com.riskcontrol.entity.RiskCase;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.RiskCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Service for AI-powered risk analysis.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AIService {
    
    private final AIClient aiClient;
    private final RiskCaseRepository riskCaseRepository;
    private final AIDecisionRecordRepository aiDecisionRecordRepository;
    private final CaseAuditLogService caseAuditLogService;
    private final ObjectMapper objectMapper;
    
    /**
     * Analyze a risk case using AI.
     *
     * @param caseId Case ID
     * @param promptVersion Prompt version (optional)
     * @return AI analysis result
     */
    public AIAnalysisDTO analyzeCase(Long caseId, String promptVersion) {
        try {
            // Get risk case
            RiskCase riskCase = riskCaseRepository.findById(caseId)
                .orElseThrow(() -> new RuntimeException("Risk case not found: " + caseId));
            
            // Prepare case data
            Map<String, Object> caseData = prepareCaseData(riskCase);
            
            // Call AI service
            AIAnalysisDTO analysis = aiClient.analyzeCase(caseId, caseData, promptVersion);
            
            log.info("AI Analysis received: riskLevel={}, reasoning={}, keyRiskPoints={}", 
                analysis.getRiskLevel(), analysis.getReasoning(), analysis.getKeyRiskPoints());
            
            // Save AI decision record (without transaction)
            saveAIDecisionRecord(riskCase, analysis, promptVersion);
            
            return analysis;
        
        } catch (Exception e) {
            log.error("Error analyzing case: {}", caseId, e);
            throw new RuntimeException("Error analyzing case: " + e.getMessage());
        }
    }
    
    /**
     * Prepare case data for AI analysis.
     */
    private Map<String, Object> prepareCaseData(RiskCase riskCase) {
        Map<String, Object> caseData = new HashMap<>();
        
        caseData.put("id", riskCase.getId());
        caseData.put("amount", riskCase.getAmount());
        caseData.put("currency", riskCase.getCurrency());
        caseData.put("country", riskCase.getCountry());
        caseData.put("device_risk", riskCase.getDeviceRisk());
        caseData.put("user_label", riskCase.getUserLabel());
        caseData.put("user_id", riskCase.getUserId());
        caseData.put("risk_level", riskCase.getRiskLevel());
        caseData.put("risk_score", riskCase.getRiskScore());
        caseData.put("rule_engine_score", riskCase.getRuleEngineScore());
        caseData.put("triggered_rules", riskCase.getTriggeredRules());

        // Add risk features if available
        if (riskCase.getRiskFeatures() != null) {
            caseData.put("risk_features", riskCase.getRiskFeatures());
        }
        
        return caseData;
    }
    
    /**
     * Save AI decision record.
     */
    @Transactional
    public void saveAIDecisionRecord(RiskCase riskCase, AIAnalysisDTO analysis, String promptVersion) {
        try {
            String normalizedRiskLevel = normalizeRiskLevel(analysis.getRiskLevel());
            String normalizedAction = normalizeSuggestedAction(analysis.getSuggestedAction());

            AIDecisionRecord record = AIDecisionRecord.builder()
                .caseId(riskCase.getId())
                .riskLevel(normalizedRiskLevel)
                .confidenceScore(analysis.getConfidenceScore())
                .suggestedAction(normalizedAction)
                .keyRiskPoints(String.join(", ", analysis.getKeyRiskPoints() != null ? analysis.getKeyRiskPoints() : java.util.List.of()))
                .reasoning(analysis.getReasoning())
                .similarCasesAnalysis(analysis.getSimilarCasesAnalysis())
                .similarCasesDetails(toJson(analysis.getSimilarCasesDetails()))
                .ruleEngineAlignment(analysis.getRuleEngineAlignment())
                .promptVersion(promptVersion != null ? promptVersion : "v1")
                .analysisSource(analysis.getAnalysisSource())
                .analysisModel(analysis.getAnalysisModel())
                .totalTimeMs(analysis.getTotalTimeMs())
                .createdAt(LocalDateTime.now())
                .build();
            
            AIDecisionRecord savedRecord = aiDecisionRecordRepository.save(record);
            
            // Update RiskCase with aiDecisionId
            riskCase.setAiDecisionId(savedRecord.getId());
            riskCaseRepository.save(riskCase);
            
            // Log ANALYZE operation
            Map<String, Object> analysisData = new HashMap<>();
            analysisData.put("riskLevel", normalizedRiskLevel);
            analysisData.put("confidenceScore", analysis.getConfidenceScore());
            analysisData.put("suggestedAction", normalizedAction);
            analysisData.put("analysisSource", analysis.getAnalysisSource());
            analysisData.put("analysisModel", analysis.getAnalysisModel());
            analysisData.put("totalTimeMs", analysis.getTotalTimeMs());
            caseAuditLogService.recordAuditLog(riskCase.getId(), "ANALYZE", null, "AI Analysis Completed", null, analysisData);
            
            log.info("AI decision record saved for case: {} with ID: {}", riskCase.getId(), savedRecord.getId());
        
        } catch (Exception e) {
            log.error("Error saving AI decision record", e);
            // Don't throw exception, just log it
        }
    }

    private String toJson(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException e) {
            log.warn("Failed to serialize JSON field for AI decision record", e);
            return null;
        }
    }

    private String normalizeRiskLevel(String raw) {
        if (raw == null) return "MEDIUM";
        String value = raw.trim().toUpperCase();
        return switch (value) {
            case "LOW", "MEDIUM", "HIGH" -> value;
            default -> "MEDIUM";
        };
    }

    private String normalizeSuggestedAction(String raw) {
        if (raw == null) return "MANUAL_REVIEW";
        String value = raw.trim().toUpperCase().replace('-', '_').replace(' ', '_');
        if (value.contains("REJECT") || value.contains("BLOCK")) return "REJECT";
        if (value.contains("APPROVE")) return "APPROVE";
        if (value.contains("REVIEW")) return "MANUAL_REVIEW";
        return "MANUAL_REVIEW";
    }
}
