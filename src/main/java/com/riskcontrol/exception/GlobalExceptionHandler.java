package com.riskcontrol.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.ServletWebRequest;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleResourceNotFoundException(
            ResourceNotFoundException ex, WebRequest request) {
        log.warn("Resource not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.NOT_FOUND, "NOT_FOUND", ex.getMessage(), null, request);
    }

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<Map<String, Object>> handleBusinessException(
            BusinessException ex, WebRequest request) {
        log.warn("Business exception: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.BAD_REQUEST, "BUSINESS_ERROR", ex.getMessage(), null, request);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex, WebRequest request) {
        log.warn("Validation error: {}", ex.getMessage());

        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
            errors.put(error.getField(), error.getDefaultMessage())
        );

        return buildErrorResponse(
            HttpStatus.BAD_REQUEST,
            "INVALID_REQUEST",
            "Validation failed",
            errors,
            request
        );
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgumentException(
            IllegalArgumentException ex, WebRequest request) {
        log.warn("Illegal argument: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.BAD_REQUEST, "INVALID_REQUEST", ex.getMessage(), null, request);
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<Map<String, Object>> handleRuntimeException(
            RuntimeException ex, WebRequest request) {
        log.error("Runtime exception: ", ex);
        return buildErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            ex.getMessage() != null ? ex.getMessage() : "An error occurred",
            null,
            request
        );
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGlobalException(
            Exception ex, WebRequest request) {
        log.error("Unexpected error: ", ex);
        return buildErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred",
            null,
            request
        );
    }

    private ResponseEntity<Map<String, Object>> buildErrorResponse(
        HttpStatus status,
        String code,
        String message,
        Map<String, ?> details,
        WebRequest request
    ) {
        LinkedHashMap<String, Object> response = new LinkedHashMap<>();
        response.put("status", "error");
        response.put("message", message);
        response.put("code", code);
        response.put("timestamp", LocalDateTime.now());
        response.put("path", request.getDescription(false).replace("uri=", ""));
        if (details != null && !details.isEmpty()) {
            response.put("details", details);
        }

        if (request instanceof ServletWebRequest servletWebRequest) {
            Object traceId = servletWebRequest.getRequest().getAttribute("traceId");
            if (traceId != null) {
                response.put("traceId", String.valueOf(traceId));
            }
        }

        return new ResponseEntity<>(response, status);
    }
}
