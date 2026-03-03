package com.riskcontrol.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * Configuration for RestTemplate.
 */
@Configuration
public class RestTemplateConfig {

    @Value("${ai.service.timeout:120000}")
    private int aiServiceTimeoutMs;
    
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(Duration.ofSeconds(5))
            .setReadTimeout(Duration.ofMillis(aiServiceTimeoutMs))
            .build();
    }
}
