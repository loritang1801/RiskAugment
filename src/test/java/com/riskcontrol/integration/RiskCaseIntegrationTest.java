package com.riskcontrol.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.service.RiskCaseService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
@ActiveProfiles("test")
@Transactional
class RiskCaseIntegrationTest {

    @Autowired
    private RiskCaseService riskCaseService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testCreateAndApproveWorkflow() {
        CreateRiskCaseRequest request = CreateRiskCaseRequest.builder()
            .bizTransactionId("IT_" + UUID.randomUUID())
            .amount(new BigDecimal("1000.00"))
            .currency("USD")
            .riskFeatures(objectMapper.createObjectNode())
            .riskScore(new BigDecimal("0.30"))
            .riskLevel("LOW")
            .riskStatus("PENDING")
            .build();

        RiskCaseDTO created = riskCaseService.createRiskCase(request);
        assertNotNull(created.getId());
        assertEquals("PENDING", created.getRiskStatus());

        RiskCaseDTO approved = riskCaseService.approveRiskCase(created.getId(), "admin");
        assertEquals("APPROVED", approved.getRiskStatus());
    }
}
