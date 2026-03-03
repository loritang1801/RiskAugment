package com.riskcontrol.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.AIAnalysisDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Client for calling Python AI service.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AIClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url:http://localhost:5000}")
    private String aiServiceUrl;

    @Value("${ai.service.fail-on-error:true}")
    private boolean failOnError;

    /**
     * Analyze a risk case using AI service.
     *
     * @param caseId Case ID
     * @param caseData Case data
     * @param promptVersion Prompt version (optional)
     * @return AI analysis result
     */
    public AIAnalysisDTO analyzeCase(Long caseId, Map<String, Object> caseData, String promptVersion) {
        try {
            String url = aiServiceUrl + "/api/ai/analyze";

            // Build request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("case_id", caseId);
            requestBody.put("case_data", caseData);
            if (promptVersion != null) {
                requestBody.put("prompt_version", promptVersion);
            }

            // Create HTTP headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // Create HTTP entity
            HttpEntity<String> entity = new HttpEntity<>(
                objectMapper.writeValueAsString(requestBody),
                headers
            );

            // Call AI service
            long startTime = System.currentTimeMillis();
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            long duration = System.currentTimeMillis() - startTime;

            log.info("AI service call completed in {}ms", duration);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();

                if ("success".equals(responseBody.get("status"))) {
                    Map<String, Object> data = (Map<String, Object>) responseBody.get("data");
                    Map<String, Object> analysis = (Map<String, Object>) data.get("analysis");

                    return parseAnalysis(analysis);
                }
            }

            log.error("AI service returned error: {}", response.getBody());
            if (failOnError) {
                throw new RuntimeException("AI service returned non-success response");
            }
            return getDefaultAnalysis();

        } catch (Exception e) {
            log.error("Error calling AI service", e);
            if (failOnError) {
                throw new RuntimeException("AI service call failed: " + e.getMessage(), e);
            }
            return getDefaultAnalysis();
        }
    }

    /**
     * Parse AI analysis from response.
     */
    private AIAnalysisDTO parseAnalysis(Map<String, Object> analysis) {
        try {
            if (analysis == null || analysis.isEmpty()) {
                return getDefaultAnalysis();
            }

            Map<String, Object> normalized = normalizeAnalysisMap(analysis);
            Integer totalTimeMs = extractTotalTimeMs(normalized);
            if (totalTimeMs != null) {
                normalized.put("total_time_ms", totalTimeMs);
            }
            log.info("Parsing analysis: {}", analysis);
            AIAnalysisDTO result = objectMapper.convertValue(normalized, AIAnalysisDTO.class);

            // Final safety defaults to keep downstream persistence stable.
            if (result.getRiskLevel() == null || result.getRiskLevel().isBlank()) {
                result.setRiskLevel("HIGH");
            }
            if (result.getSuggestedAction() == null || result.getSuggestedAction().isBlank()) {
                result.setSuggestedAction("MANUAL_REVIEW");
            }
            if (result.getConfidenceScore() == null) {
                result.setConfidenceScore(java.math.BigDecimal.valueOf(0.3));
            }
            result.setKeyRiskPoints(sanitizeRiskPoints(result.getKeyRiskPoints()));
            if (result.getKeyRiskPoints().isEmpty()) {
                result.setKeyRiskPoints(List.of("风险证据不足，建议结合规则评分与历史相似案例复核"));
            }
            if (result.getReasoning() == null || result.getReasoning().isBlank() || isTechnicalReasoning(result.getReasoning()) || isGarbledText(result.getReasoning())) {
                result.setReasoning("AI 已完成本次分析，当前结论主要基于规则评分与历史相似案例，建议结合关键风险点进行复核。");
            }
            if (result.getAnalysisSource() == null || result.getAnalysisSource().isBlank()) {
                result.setAnalysisSource("AI Service");
            }
            if (result.getAnalysisModel() == null || result.getAnalysisModel().isBlank()) {
                result.setAnalysisModel("unknown");
            }

            log.info("Parsed result: riskLevel={}, reasoning={}, keyRiskPoints={}, analysisSource={}",
                result.getRiskLevel(), result.getReasoning(), result.getKeyRiskPoints(), result.getAnalysisSource());
            return result;
        } catch (Exception e) {
            log.error("Error parsing AI analysis", e);
            return getDefaultAnalysis();
        }
    }

    private Map<String, Object> normalizeAnalysisMap(Map<String, Object> analysis) {
        Map<String, Object> normalized = new HashMap<>(analysis);

        moveIfPresent(normalized, "riskLevel", "risk_level");
        moveIfPresent(normalized, "confidenceScore", "confidence_score");
        moveIfPresent(normalized, "keyRiskPoints", "key_risk_points");
        moveIfPresent(normalized, "suggestedAction", "suggested_action");
        moveIfPresent(normalized, "similarCasesAnalysis", "similar_cases_analysis");
        moveIfPresent(normalized, "similarCasesDetails", "similar_cases_details");
        moveIfPresent(normalized, "ruleEngineAlignment", "rule_engine_alignment");
        moveIfPresent(normalized, "confidenceExplanation", "confidence_explanation");
        moveIfPresent(normalized, "alternativeView", "alternative_view");
        moveIfPresent(normalized, "analysisSource", "analysis_source");
        moveIfPresent(normalized, "analysisModel", "analysis_model");
        moveIfPresent(normalized, "totalTimeMs", "total_time_ms");

        return normalized;
    }

    private Integer extractTotalTimeMs(Map<String, Object> analysis) {
        Integer direct = toInteger(analysis.get("total_time_ms"));
        if (direct != null) {
            return direct;
        }

        Object executionMetricsObj = analysis.get("execution_metrics");
        if (executionMetricsObj instanceof Map<?, ?> executionMetrics) {
            Integer fromExecution = toInteger(executionMetrics.get("total_time_ms"));
            if (fromExecution != null) {
                return fromExecution;
            }
        }

        Object metadataObj = analysis.get("metadata");
        if (metadataObj instanceof Map<?, ?> metadata) {
            return toInteger(metadata.get("total_time_ms"));
        }

        return null;
    }

    private Integer toInteger(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value instanceof String stringValue) {
            try {
                return Integer.parseInt(stringValue.trim());
            } catch (NumberFormatException ignored) {
                return null;
            }
        }
        return null;
    }

    private void moveIfPresent(Map<String, Object> map, String sourceKey, String targetKey) {
        if (map.containsKey(sourceKey)) {
            if (!map.containsKey(targetKey)) {
                map.put(targetKey, map.get(sourceKey));
            }
            map.remove(sourceKey);
        }
    }

    private List<String> sanitizeRiskPoints(List<String> points) {
        if (points == null || points.isEmpty()) {
            return new ArrayList<>();
        }

        List<String> sanitized = new ArrayList<>();
        for (String point : points) {
            if (point == null || point.isBlank()) {
                continue;
            }
            String p = point.trim();
            String lower = p.toLowerCase(Locale.ROOT);
            boolean internalNoise =
                lower.contains("llm") ||
                lower.contains("parse") ||
                lower.contains("json") ||
                lower.contains("calibrated by") ||
                isGarbledText(p) ||
                p.contains("模型输出结构异常") ||
                p.contains("无法解析") ||
                p.contains("默认结果");
            if (!internalNoise) {
                sanitized.add(p);
            }
            if (sanitized.size() >= 3) {
                break;
            }
        }
        return sanitized;
    }

    private boolean isTechnicalReasoning(String reasoning) {
        String lower = reasoning.toLowerCase(Locale.ROOT);
        return lower.contains("without detailed reasoning")
            || lower.contains("parse")
            || lower.contains("json")
            || reasoning.contains("无法解析")
            || reasoning.contains("默认结果")
            || reasoning.contains("结构化校验");
    }

    private boolean isGarbledText(String text) {
        if (text == null || text.isBlank()) {
            return false;
        }
        String value = text.trim();
        if (value.contains("???")) {
            return true;
        }
        long qCount = value.chars().filter(ch -> ch == '?').count();
        return qCount >= 3 && qCount * 1.0 / Math.max(1, value.length()) > 0.2;
    }

    /**
     * Get default analysis when AI service fails.
     */
    private AIAnalysisDTO getDefaultAnalysis() {
        return AIAnalysisDTO.builder()
            .riskLevel("HIGH")
            .confidenceScore(java.math.BigDecimal.valueOf(0.3))
            .suggestedAction("MANUAL_REVIEW")
            .keyRiskPoints(java.util.List.of("AI 服务当前不可用，建议人工复核"))
            .reasoning("AI 服务处理异常，系统已降级，请人工复核。")
            .build();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getChainHealthMetrics(int limit) {
        try {
            int safeLimit = Math.max(1, Math.min(limit, 500));
            String url = aiServiceUrl + "/api/ai/metrics/health?limit=" + safeLimit;
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.GET, HttpEntity.EMPTY, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                if ("success".equals(body.get("status")) && body.get("data") instanceof Map<?, ?> data) {
                    return (Map<String, Object>) data;
                }
            }
            log.warn("AI service health metrics returned non-success: {}", response.getBody());
        } catch (Exception e) {
            log.warn("Failed to fetch AI chain health metrics: {}", e.getMessage());
        }

        Map<String, Object> fallback = new HashMap<>();
        fallback.put("window_size", limit);
        fallback.put("total_requests", 0);
        fallback.put("success_requests", 0);
        fallback.put("failed_requests", 0);
        fallback.put("failure_rate", 1.0);
        fallback.put("error_categories", Map.of("upstream_unavailable", 1));
        fallback.put("latency_ms", Map.of("avg", 0, "p50", 0, "p95", 0, "max", 0));
        fallback.put(
            "stage_avg_ms",
            Map.of("rule", 0, "retrieval", 0, "similar_analysis", 0, "transaction_history", 0, "llm", 0, "total", 0)
        );
        fallback.put("degraded", true);
        return fallback;
    }

}
