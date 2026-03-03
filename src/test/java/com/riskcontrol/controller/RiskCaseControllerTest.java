package com.riskcontrol.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.service.AIService;
import com.riskcontrol.service.RiskCaseService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@ActiveProfiles("test")
@AutoConfigureMockMvc
@WithMockUser(username = "admin", roles = {"ADMIN"})
class RiskCaseControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private RiskCaseService riskCaseService;

    @MockBean
    private AIService aiService;

    private RiskCaseDTO riskCaseDTO;
    private CreateRiskCaseRequest createRequest;

    @BeforeEach
    void setUp() {
        riskCaseDTO = RiskCaseDTO.builder()
            .id(1L)
            .bizTransactionId("TXN_001")
            .amount(new BigDecimal("1000.00"))
            .currency("USD")
            .riskScore(new BigDecimal("0.30"))
            .riskLevel("LOW")
            .riskStatus("PENDING")
            .build();

        createRequest = CreateRiskCaseRequest.builder()
            .bizTransactionId("TXN_001")
            .amount(new BigDecimal("1000.00"))
            .currency("USD")
            .riskScore(new BigDecimal("0.30"))
            .riskLevel("LOW")
            .riskStatus("PENDING")
            .riskFeatures(objectMapper.createObjectNode())
            .build();
    }

    @Test
    void testCreateRiskCase_Success() throws Exception {
        when(riskCaseService.createRiskCase(any(CreateRiskCaseRequest.class))).thenReturn(riskCaseDTO);

        mockMvc.perform(post("/api/cases")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(createRequest)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.id").value(1L))
            .andExpect(jsonPath("$.data.bizTransactionId").value("TXN_001"));
    }

    @Test
    void testGetRiskCaseById_Success() throws Exception {
        when(riskCaseService.getRiskCaseById(1L)).thenReturn(riskCaseDTO);

        mockMvc.perform(get("/api/cases/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.id").value(1L));
    }

    @Test
    void testListRiskCases_Success() throws Exception {
        Page<RiskCaseDTO> page = new PageImpl<>(List.of(riskCaseDTO));
        when(riskCaseService.listRiskCases(0, 10)).thenReturn(page);

        mockMvc.perform(get("/api/cases?page=0&size=10"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data[0].id").value(1L));
    }

    @Test
    void testUpdateRiskCase_Success() throws Exception {
        when(riskCaseService.updateRiskCase(eq(1L), any(CreateRiskCaseRequest.class))).thenReturn(riskCaseDTO);

        mockMvc.perform(put("/api/cases/1")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(createRequest)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.id").value(1L));
    }

    @Test
    void testApproveRiskCase_Success() throws Exception {
        riskCaseDTO.setRiskStatus("APPROVED");
        when(riskCaseService.approveRiskCase(1L, "admin")).thenReturn(riskCaseDTO);

        mockMvc.perform(put("/api/cases/1/approve"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.riskStatus").value("APPROVED"));
    }

    @Test
    void testRejectRiskCase_Success() throws Exception {
        riskCaseDTO.setRiskStatus("REJECTED");
        when(riskCaseService.rejectRiskCase(1L, "admin")).thenReturn(riskCaseDTO);

        mockMvc.perform(put("/api/cases/1/reject"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.riskStatus").value("REJECTED"));
    }

    @Test
    void testDeleteRiskCase_Success() throws Exception {
        mockMvc.perform(delete("/api/cases/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"));
    }
}
