package com.riskcontrol.service;

import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.entity.RiskCase;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.RiskCaseRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class RiskCaseServiceTest {

    @Mock
    private RiskCaseRepository riskCaseRepository;

    @Mock
    private CaseAuditLogService caseAuditLogService;

    @Mock
    private AIDecisionRecordRepository aiDecisionRecordRepository;

    @InjectMocks
    private RiskCaseService riskCaseService;

    private RiskCase testRiskCase;
    private CreateRiskCaseRequest createRequest;

    @BeforeEach
    void setUp() {
        testRiskCase = RiskCase.builder()
            .id(1L)
            .bizTransactionId("TXN_001")
            .amount(new BigDecimal("1000.00"))
            .currency("USD")
            .riskScore(new BigDecimal("0.30"))
            .riskLevel("LOW")
            .riskStatus("PENDING")
            .build();

        createRequest = CreateRiskCaseRequest.builder()
            .bizTransactionId("TXN_002")
            .amount(new BigDecimal("2000.00"))
            .currency("USD")
            .riskScore(new BigDecimal("0.60"))
            .riskLevel("MEDIUM")
            .riskStatus("PENDING")
            .build();
    }

    @Test
    void testCreateRiskCase_Success() {
        when(riskCaseRepository.findByBizTransactionId(createRequest.getBizTransactionId()))
            .thenReturn(Optional.empty());
        when(riskCaseRepository.save(any(RiskCase.class))).thenReturn(testRiskCase);

        RiskCaseDTO result = riskCaseService.createRiskCase(createRequest);

        assertNotNull(result);
        assertEquals(1L, result.getId());
        verify(riskCaseRepository, times(1)).save(any(RiskCase.class));
        verify(caseAuditLogService, times(1)).logOperation(any(), any(), any(), any(), any());
    }

    @Test
    void testCreateRiskCase_DuplicateTransactionId() {
        when(riskCaseRepository.findByBizTransactionId(createRequest.getBizTransactionId()))
            .thenReturn(Optional.of(testRiskCase));

        assertThrows(IllegalArgumentException.class, () -> riskCaseService.createRiskCase(createRequest));
        verify(riskCaseRepository, never()).save(any(RiskCase.class));
    }

    @Test
    void testGetRiskCaseById_NotFound() {
        when(riskCaseRepository.findById(anyLong())).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> riskCaseService.getRiskCaseById(999L));
    }

    @Test
    void testListRiskCases_Success() {
        Page<RiskCase> page = new PageImpl<>(List.of(testRiskCase));
        when(riskCaseRepository.findAll(any(Pageable.class))).thenReturn(page);

        Page<RiskCaseDTO> result = riskCaseService.listRiskCases(0, 10);
        assertEquals(1, result.getTotalElements());
    }
}
