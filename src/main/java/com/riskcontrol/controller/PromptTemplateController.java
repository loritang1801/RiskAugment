package com.riskcontrol.controller;

import com.riskcontrol.dto.PromptTemplateDTO;
import com.riskcontrol.service.PromptTemplateService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Controller for Prompt Template management.
 */
@Slf4j
@RestController
@RequestMapping("/api/prompts")
@RequiredArgsConstructor
@Tag(name = "Prompt Management", description = "APIs for prompt template management")
public class PromptTemplateController {
    
    private final PromptTemplateService promptTemplateService;
    
    @GetMapping
    @Operation(summary = "Get all prompt templates")
    public ResponseEntity<Map<String, Object>> getAllPrompts() {
        log.info("Getting all prompt templates");
        
        List<PromptTemplateDTO> prompts = promptTemplateService.getAllPrompts();
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompts);
        response.put("total", prompts.size());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/active")
    @Operation(summary = "Get active prompt template")
    public ResponseEntity<Map<String, Object>> getActivePrompt() {
        log.info("Getting active prompt template");
        
        PromptTemplateDTO prompt = promptTemplateService.getActivePrompt();
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompt);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{version}")
    @Operation(summary = "Get prompt template by version")
    public ResponseEntity<Map<String, Object>> getPromptByVersion(@PathVariable String version) {
        log.info("Getting prompt template: {}", version);
        
        PromptTemplateDTO prompt = promptTemplateService.getPromptByVersion(version);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompt);
        
        return ResponseEntity.ok(response);
    }
    
    @PostMapping
    @Operation(summary = "Create new prompt template")
    public ResponseEntity<Map<String, Object>> createPrompt(@Valid @RequestBody PromptTemplateDTO dto) {
        log.info("Creating prompt template: {}", dto.getVersion());
        
        PromptTemplateDTO prompt = promptTemplateService.createPrompt(dto);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompt);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    @PutMapping("/{version}")
    @Operation(summary = "Update prompt template")
    public ResponseEntity<Map<String, Object>> updatePrompt(
        @PathVariable String version,
        @Valid @RequestBody PromptTemplateDTO dto
    ) {
        log.info("Updating prompt template: {}", version);
        
        PromptTemplateDTO prompt = promptTemplateService.updatePrompt(version, dto);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompt);
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{version}/activate")
    @Operation(summary = "Activate prompt template")
    public ResponseEntity<Map<String, Object>> activatePrompt(@PathVariable String version) {
        log.info("Activating prompt template: {}", version);
        
        PromptTemplateDTO prompt = promptTemplateService.activatePrompt(version);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", prompt);
        response.put("message", "Prompt template activated successfully");
        
        return ResponseEntity.ok(response);
    }
    
    @DeleteMapping("/{version}")
    @Operation(summary = "Delete prompt template")
    public ResponseEntity<Map<String, Object>> deletePrompt(@PathVariable String version) {
        log.info("Deleting prompt template: {}", version);
        
        promptTemplateService.deletePrompt(version);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "Prompt template deleted successfully");
        
        return ResponseEntity.ok(response);
    }
}
