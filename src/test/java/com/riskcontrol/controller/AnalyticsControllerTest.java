package com.riskcontrol.controller;

import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.service.AnalyticsService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@ActiveProfiles("test")
@AutoConfigureMockMvc
@WithMockUser(username = "admin", roles = {"ADMIN"})
class AnalyticsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AnalyticsService analyticsService;

    @MockBean
    private AIDecisionRecordRepository aiDecisionRecordRepository;

    @Test
    void testGetReviewEfficiency_Success() throws Exception {
        when(analyticsService.getReviewEfficiency(any(), any()))
            .thenReturn(Map.of(
                "averageReviewTime", 3500L,
                "totalCases", 100L,
                "minTime", 1000L,
                "maxTime", 9000L
            ));

        mockMvc.perform(get("/api/analytics/review-efficiency"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.totalCases").value(100))
            .andExpect(jsonPath("$.data.averageReviewTime").value(3500));
    }

    @Test
    void testGetOverrideRate_Success() throws Exception {
        when(analyticsService.getOverrideRate(any(), any()))
            .thenReturn(Map.of(
                "overrideRate", 0.15,
                "totalDecisions", 20L,
                "overrideCount", 3L
            ));

        mockMvc.perform(get("/api/analytics/override-rate"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.overrideRate").value(0.15));
    }

    @Test
    void testGetPromptComparison_Success() throws Exception {
        when(analyticsService.getPromptVersionComparison(any(), any()))
            .thenReturn(Map.of("versions", java.util.List.of(), "count", 0));

        mockMvc.perform(get("/api/analytics/prompt-comparison"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.count").value(0));
    }
}
