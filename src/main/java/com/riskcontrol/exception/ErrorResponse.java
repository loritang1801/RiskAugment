package com.riskcontrol.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 统一的错误响应格式
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {
    
    /**
     * 错误代码
     */
    private String code;
    
    /**
     * 错误消息
     */
    private String message;
    
    /**
     * 时间戳
     */
    private LocalDateTime timestamp;
    
    /**
     * 请求路径
     */
    private String path;
    
    /**
     * 详细信息（可选）
     */
    private Map<String, ?> details;
}
