package com.riskcontrol.config;

import com.riskcontrol.exception.ErrorResponse;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.http.server.ServletServerHttpRequest;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class ApiResponseAdvice implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(
        MethodParameter returnType,
        Class<? extends HttpMessageConverter<?>> converterType
    ) {
        return true;
    }

    @Override
    public Object beforeBodyWrite(
        Object body,
        MethodParameter returnType,
        MediaType selectedContentType,
        Class<? extends HttpMessageConverter<?>> selectedConverterType,
        ServerHttpRequest request,
        ServerHttpResponse response
    ) {
        String traceId = null;
        if (request instanceof ServletServerHttpRequest servletRequest) {
            Object trace = servletRequest.getServletRequest().getAttribute(TraceIdFilter.TRACE_ID_ATTR);
            if (trace != null) {
                traceId = String.valueOf(trace);
            }
        }

        if (body instanceof Map<?, ?> mapBody) {
            if (!mapBody.containsKey("status")) {
                return body;
            }
            LinkedHashMap<String, Object> enriched = new LinkedHashMap<>();
            mapBody.forEach((k, v) -> enriched.put(String.valueOf(k), v));
            enriched.putIfAbsent("timestamp", LocalDateTime.now());
            if (traceId != null && !traceId.isBlank()) {
                enriched.putIfAbsent("traceId", traceId);
            }
            return enriched;
        }

        if (body instanceof ErrorResponse error) {
            LinkedHashMap<String, Object> normalized = new LinkedHashMap<>();
            normalized.put("status", "error");
            normalized.put("message", error.getMessage());
            normalized.put("code", error.getCode());
            normalized.put("details", error.getDetails());
            normalized.put("path", error.getPath());
            normalized.put("timestamp", error.getTimestamp() != null ? error.getTimestamp() : LocalDateTime.now());
            if (traceId != null && !traceId.isBlank()) {
                normalized.put("traceId", traceId);
            }
            return normalized;
        }

        return body;
    }
}
