package com.riskcontrol.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.AIAnalysisDTO;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.startsWith;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AIClientTest {

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    private AIClient aiClient;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(aiClient, "objectMapper", new ObjectMapper());
        ReflectionTestUtils.setField(aiClient, "aiServiceUrl", "http://localhost:5000");
    }

    @Test
    void analyzeCase_shouldParseSnakeCaseResponse() {
        Map<String, Object> analysis = new HashMap<>();
        analysis.put("risk_level", "LOW");
        analysis.put("confidence_score", 0.91);
        analysis.put("suggested_action", "APPROVE");
        analysis.put("key_risk_points", List.of("normal amount"));
        analysis.put("reasoning", "Risk is low.");
        analysis.put("analysis_source", "ChatGPT");
        analysis.put("analysis_model", "gpt-4o-mini");

        Map<String, Object> data = new HashMap<>();
        data.put("analysis", analysis);
        Map<String, Object> body = new HashMap<>();
        body.put("status", "success");
        body.put("data", data);

        when(restTemplate.postForEntity(startsWith("http://localhost:5000"), any(HttpEntity.class), eq(Map.class)))
            .thenReturn(new ResponseEntity<>(body, HttpStatus.OK));

        AIAnalysisDTO result = aiClient.analyzeCase(1L, Map.of("amount", 100), null);

        assertEquals("LOW", result.getRiskLevel());
        assertEquals("APPROVE", result.getSuggestedAction());
        assertEquals("ChatGPT", result.getAnalysisSource());
        assertNotNull(result.getConfidenceScore());
    }

    @Test
    void analyzeCase_shouldNormalizeCamelCaseResponse() {
        Map<String, Object> analysis = new HashMap<>();
        analysis.put("riskLevel", "MEDIUM");
        analysis.put("confidenceScore", 0.66);
        analysis.put("suggestedAction", "REVIEW");
        analysis.put("keyRiskPoints", List.of("velocity anomaly"));
        analysis.put("reasoning", "Needs review");
        analysis.put("analysisSource", "Rule-Based");
        analysis.put("analysisModel", "rule-engine");

        Map<String, Object> data = new HashMap<>();
        data.put("analysis", analysis);
        Map<String, Object> body = new HashMap<>();
        body.put("status", "success");
        body.put("data", data);

        when(restTemplate.postForEntity(startsWith("http://localhost:5000"), any(HttpEntity.class), eq(Map.class)))
            .thenReturn(new ResponseEntity<>(body, HttpStatus.OK));

        AIAnalysisDTO result = aiClient.analyzeCase(2L, Map.of("amount", 50000), "v1");

        assertEquals("MEDIUM", result.getRiskLevel());
        assertEquals("REVIEW", result.getSuggestedAction());
        assertEquals("Rule-Based", result.getAnalysisSource());
        assertNotNull(result.getKeyRiskPoints());
    }

    @Test
    void analyzeCase_shouldFallbackWhenAiServiceFails() {
        when(restTemplate.postForEntity(startsWith("http://localhost:5000"), any(HttpEntity.class), eq(Map.class)))
            .thenThrow(new RuntimeException("connection failed"));

        AIAnalysisDTO result = aiClient.analyzeCase(3L, Map.of("amount", 99999), null);

        assertEquals("HIGH", result.getRiskLevel());
        assertEquals("MANUAL_REVIEW", result.getSuggestedAction());
        assertNotNull(result.getKeyRiskPoints());
    }
}
