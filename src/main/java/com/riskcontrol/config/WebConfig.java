package com.riskcontrol.config;

import org.springframework.format.FormatterRegistry;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Web configuration for custom formatters and converters.
 */
@Component
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void addFormatters(FormatterRegistry registry) {
        // Add custom LocalDateTime formatter to handle both ISO format and custom format
        registry.addConverter(String.class, LocalDateTime.class, source -> {
            if (source == null || source.isEmpty()) {
                return null;
            }
            
            // Try ISO format first (2026-02-27T16:58:58)
            try {
                return LocalDateTime.parse(source, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            } catch (Exception e1) {
                // Try custom format (2026-01-28 16:58:58)
                try {
                    return LocalDateTime.parse(source, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
                } catch (Exception e2) {
                    // Try another format (2026-01-28)
                    try {
                        return LocalDateTime.parse(source + " 00:00:00", DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
                    } catch (Exception e3) {
                        throw new IllegalArgumentException("Unable to parse date: " + source);
                    }
                }
            }
        });
    }
}
