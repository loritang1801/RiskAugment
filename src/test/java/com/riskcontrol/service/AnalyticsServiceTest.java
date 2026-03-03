package com.riskcontrol.service;

import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.CaseAuditLogRepository;
import com.riskcontrol.repository.PromptTemplateRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.sql.Date;
import java.time.LocalDate;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AnalyticsServiceTest {

    @Mock
    private AIDecisionRecordRepository aiDecisionRecordRepository;

    @Mock
    private CaseAuditLogRepository caseAuditLogRepository;

    @Mock
    private PromptTemplateRepository promptTemplateRepository;

    @InjectMocks
    private AnalyticsService analyticsService;

    @Test
    void testGetReviewEfficiency() {
        when(aiDecisionRecordRepository.getReviewEfficiencyStats(null, null))
            .thenReturn(Collections.singletonList(new Object[]{3500.0, 10L, 1000L, 5000L}));

        Map<String, Object> result = analyticsService.getReviewEfficiency(null, null);

        assertNotNull(result);
        assertEquals(3500L, result.get("averageReviewTime"));
        assertEquals(10L, result.get("totalCases"));
        assertEquals(1000L, result.get("minTime"));
        assertEquals(5000L, result.get("maxTime"));
    }

    @Test
    void testGetOverrideRate() {
        when(aiDecisionRecordRepository.getOverrideRateStats(null, null))
            .thenReturn(Collections.singletonList(new Object[]{20L, 5L}));

        Map<String, Object> result = analyticsService.getOverrideRate(null, null);

        assertNotNull(result);
        assertEquals(20L, result.get("totalDecisions"));
        assertEquals(5L, result.get("overrideCount"));
        assertEquals(0.25, (Double) result.get("overrideRate"), 0.0001);
    }

    @Test
    void testGetPromptVersionComparison() {
        when(aiDecisionRecordRepository.getPromptVersionComparison(null, null))
            .thenReturn(Collections.singletonList(new Object[]{"v1", 12L, 7L, 5L, 2L, 900L}));

        Map<String, Object> result = analyticsService.getPromptVersionComparison(null, null);

        assertNotNull(result);
        assertEquals(1, result.get("count"));
    }

    @Test
    @SuppressWarnings("unchecked")
    void testGetReviewEfficiencyTrend_withSqlDate() {
        when(aiDecisionRecordRepository.getReviewEfficiencyTrend(null, null))
            .thenReturn(Collections.singletonList(new Object[]{Date.valueOf("2026-03-02"), 1200L, 5L}));

        Map<String, Object> result = analyticsService.getReviewEfficiencyTrend(null, null, "day");

        List<Map<String, Object>> data = (List<Map<String, Object>>) result.get("data");
        assertEquals(1, data.size());
        assertEquals(LocalDate.of(2026, 3, 2), data.get(0).get("date"));
        assertEquals(1200L, data.get(0).get("averageTime"));
        assertEquals(5L, data.get(0).get("count"));
    }

    @Test
    @SuppressWarnings("unchecked")
    void testGetOverrideRateTrend_withStringDate() {
        when(aiDecisionRecordRepository.getOverrideRateTrend(null, null))
            .thenReturn(Collections.singletonList(new Object[]{"2026-03-01", 10L, 2L}));

        Map<String, Object> result = analyticsService.getOverrideRateTrend(null, null);

        List<Map<String, Object>> data = (List<Map<String, Object>>) result.get("data");
        assertEquals(1, data.size());
        assertEquals(LocalDate.of(2026, 3, 1), data.get(0).get("date"));
        assertEquals(0.2, (Double) data.get(0).get("overrideRate"), 0.0001);
    }

    @Test
    @SuppressWarnings("unchecked")
    void testGetReviewEfficiencyTrend_withUnknownDateType() {
        when(aiDecisionRecordRepository.getReviewEfficiencyTrend(null, null))
            .thenReturn(Collections.singletonList(new Object[]{12345L, 900L, 3L}));

        Map<String, Object> result = analyticsService.getReviewEfficiencyTrend(null, null, "day");

        List<Map<String, Object>> data = (List<Map<String, Object>>) result.get("data");
        assertEquals(1, data.size());
        assertNull(data.get(0).get("date"));
    }
}
