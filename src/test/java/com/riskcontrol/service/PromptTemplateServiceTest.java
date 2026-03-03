package com.riskcontrol.service;

import com.riskcontrol.dto.PromptTemplateDTO;
import com.riskcontrol.entity.PromptTemplate;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.repository.PromptTemplateRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class PromptTemplateServiceTest {

    @Mock
    private PromptTemplateRepository promptTemplateRepository;

    @InjectMocks
    private PromptTemplateService promptTemplateService;

    private PromptTemplate promptTemplate;
    private PromptTemplateDTO promptTemplateDTO;

    @BeforeEach
    void setUp() {
        promptTemplate = PromptTemplate.builder()
            .id(1L)
            .version("v1")
            .systemPrompt("system")
            .userPromptTemplate("user-template")
            .description("desc")
            .isActive(false)
            .build();

        promptTemplateDTO = PromptTemplateDTO.builder()
            .version("v1")
            .systemPrompt("system")
            .userPromptTemplate("user-template")
            .description("desc")
            .isActive(false)
            .build();
    }

    @Test
    void testGetAllPrompts_Success() {
        when(promptTemplateRepository.findAllByOrderByCreatedAtDesc()).thenReturn(List.of(promptTemplate));
        List<PromptTemplateDTO> result = promptTemplateService.getAllPrompts();
        assertEquals(1, result.size());
    }

    @Test
    void testGetPromptByVersion_NotFound() {
        when(promptTemplateRepository.findByVersion("v99")).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> promptTemplateService.getPromptByVersion("v99"));
    }

    @Test
    void testCreatePrompt_DuplicateVersion() {
        when(promptTemplateRepository.existsByVersion("v1")).thenReturn(true);
        assertThrows(IllegalArgumentException.class, () -> promptTemplateService.createPrompt(promptTemplateDTO));
        verify(promptTemplateRepository, never()).save(any(PromptTemplate.class));
    }

    @Test
    void testActivatePrompt_Success() {
        PromptTemplate oldActive = PromptTemplate.builder()
            .id(2L)
            .version("v0")
            .systemPrompt("old-system")
            .userPromptTemplate("old-user-template")
            .isActive(true)
            .build();

        when(promptTemplateRepository.findByVersion("v1")).thenReturn(Optional.of(promptTemplate));
        when(promptTemplateRepository.findByIsActiveTrue()).thenReturn(Optional.of(oldActive));
        when(promptTemplateRepository.save(any(PromptTemplate.class))).thenAnswer(invocation -> invocation.getArgument(0));

        PromptTemplateDTO result = promptTemplateService.activatePrompt("v1");
        assertNotNull(result);
        assertEquals("v1", result.getVersion());
        verify(promptTemplateRepository, times(2)).save(any(PromptTemplate.class));
    }
}
