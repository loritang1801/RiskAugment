package com.riskcontrol.performance;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.service.RiskCaseService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
@ActiveProfiles("test")
class PerformanceTest {

    @Autowired
    private RiskCaseService riskCaseService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testCreateRiskCasePerformance() {
        CreateRiskCaseRequest request = CreateRiskCaseRequest.builder()
            .bizTransactionId("PERF_" + UUID.randomUUID())
            .amount(new BigDecimal("5000.00"))
            .currency("USD")
            .riskFeatures(objectMapper.createObjectNode())
            .riskScore(new BigDecimal("0.70"))
            .riskLevel("HIGH")
            .riskStatus("PENDING")
            .build();

        long start = System.currentTimeMillis();
        RiskCaseDTO created = riskCaseService.createRiskCase(request);
        long duration = System.currentTimeMillis() - start;

        assertNotNull(created.getId());
        assertTrue(duration < 3000);
    }
}
