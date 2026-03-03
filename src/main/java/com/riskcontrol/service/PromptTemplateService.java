package com.riskcontrol.service;

import com.riskcontrol.dto.PromptTemplateDTO;
import com.riskcontrol.entity.PromptTemplate;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.repository.PromptTemplateRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Service for Prompt Template management.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PromptTemplateService {
    
    private final PromptTemplateRepository promptTemplateRepository;
    
    /**
     * Get all prompt templates.
     */
    public List<PromptTemplateDTO> getAllPrompts() {
        log.info("Getting all prompt templates");
        
        return promptTemplateRepository.findAllByOrderByCreatedAtDesc()
            .stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * Get prompt template by version.
     */
    public PromptTemplateDTO getPromptByVersion(String version) {
        log.info("Getting prompt template: {}", version);
        
        PromptTemplate template = promptTemplateRepository.findByVersion(version)
            .orElseThrow(() -> new ResourceNotFoundException("Prompt template not found: " + version));
        
        return convertToDTO(template);
    }
    
    /**
     * Get active prompt template.
     */
    public PromptTemplateDTO getActivePrompt() {
        log.info("Getting active prompt template");
        
        PromptTemplate template = promptTemplateRepository.findByIsActiveTrue()
            .orElseThrow(() -> new ResourceNotFoundException("No active prompt template found"));
        
        return convertToDTO(template);
    }
    
    /**
     * Create new prompt template.
     */
    @Transactional
    public PromptTemplateDTO createPrompt(PromptTemplateDTO dto) {
        log.info("Creating prompt template: {}", dto.getVersion());
        
        // Check if version already exists
        if (promptTemplateRepository.existsByVersion(dto.getVersion())) {
            throw new IllegalArgumentException("Prompt version already exists: " + dto.getVersion());
        }
        
        PromptTemplate template = PromptTemplate.builder()
            .version(dto.getVersion())
            .systemPrompt(dto.getSystemPrompt())
            .userPromptTemplate(dto.getUserPromptTemplate())
            .description(dto.getDescription())
            .isActive(false)
            .build();
        
        template = promptTemplateRepository.save(template);
        
        log.info("Prompt template created: {}", template.getVersion());
        return convertToDTO(template);
    }
    
    /**
     * Activate prompt template.
     */
    @Transactional
    public PromptTemplateDTO activatePrompt(String version) {
        log.info("Activating prompt template: {}", version);
        
        // Get the template to activate
        PromptTemplate template = promptTemplateRepository.findByVersion(version)
            .orElseThrow(() -> new ResourceNotFoundException("Prompt template not found: " + version));
        
        // Deactivate all other templates
        promptTemplateRepository.findByIsActiveTrue().ifPresent(active -> {
            active.setIsActive(false);
            promptTemplateRepository.save(active);
        });
        
        // Activate the specified template
        template.setIsActive(true);
        template = promptTemplateRepository.save(template);
        
        log.info("Prompt template activated: {}", template.getVersion());
        return convertToDTO(template);
    }
    
    /**
     * Update prompt template.
     */
    @Transactional
    public PromptTemplateDTO updatePrompt(String version, PromptTemplateDTO dto) {
        log.info("Updating prompt template: {}", version);
        
        PromptTemplate template = promptTemplateRepository.findByVersion(version)
            .orElseThrow(() -> new ResourceNotFoundException("Prompt template not found: " + version));
        
        if (dto.getSystemPrompt() != null) {
            template.setSystemPrompt(dto.getSystemPrompt());
        }
        
        if (dto.getUserPromptTemplate() != null) {
            template.setUserPromptTemplate(dto.getUserPromptTemplate());
        }
        
        if (dto.getDescription() != null) {
            template.setDescription(dto.getDescription());
        }
        
        template = promptTemplateRepository.save(template);
        
        log.info("Prompt template updated: {}", template.getVersion());
        return convertToDTO(template);
    }
    
    /**
     * Delete prompt template.
     */
    @Transactional
    public void deletePrompt(String version) {
        log.info("Deleting prompt template: {}", version);
        
        PromptTemplate template = promptTemplateRepository.findByVersion(version)
            .orElseThrow(() -> new ResourceNotFoundException("Prompt template not found: " + version));
        
        if (template.getIsActive()) {
            throw new IllegalArgumentException("Cannot delete active prompt template");
        }
        
        promptTemplateRepository.delete(template);
        
        log.info("Prompt template deleted: {}", version);
    }
    
    /**
     * Convert entity to DTO.
     */
    private PromptTemplateDTO convertToDTO(PromptTemplate template) {
        return PromptTemplateDTO.builder()
            .id(template.getId())
            .version(template.getVersion())
            .systemPrompt(template.getSystemPrompt())
            .userPromptTemplate(template.getUserPromptTemplate())
            .description(template.getDescription())
            .isActive(template.getIsActive())
            .avgResponseTimeMs(template.getAvgResponseTimeMs())
            .overrideRate(template.getOverrideRate())
            .createdAt(template.getCreatedAt())
            .updatedAt(template.getUpdatedAt())
            .build();
    }
}
