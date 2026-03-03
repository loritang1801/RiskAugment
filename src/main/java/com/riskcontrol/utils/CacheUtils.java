package com.riskcontrol.utils;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * 缓存工具类
 * 提供 Redis 缓存操作的便捷方法
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class CacheUtils {

    private final RedisTemplate<String, Object> redisTemplate;

    /**
     * 设置缓存
     */
    public void set(String key, Object value) {
        try {
            redisTemplate.opsForValue().set(key, value);
            log.debug("Cache set: {}", key);
        } catch (Exception e) {
            log.error("Failed to set cache: {}", key, e);
        }
    }

    /**
     * 设置缓存（带过期时间）
     */
    public void set(String key, Object value, long timeout, TimeUnit unit) {
        try {
            redisTemplate.opsForValue().set(key, value, timeout, unit);
            log.debug("Cache set with timeout: {} ({})", key, timeout);
        } catch (Exception e) {
            log.error("Failed to set cache with timeout: {}", key, e);
        }
    }

    /**
     * 获取缓存
     */
    public Object get(String key) {
        try {
            Object value = redisTemplate.opsForValue().get(key);
            if (value != null) {
                log.debug("Cache hit: {}", key);
            } else {
                log.debug("Cache miss: {}", key);
            }
            return value;
        } catch (Exception e) {
            log.error("Failed to get cache: {}", key, e);
            return null;
        }
    }

    /**
     * 删除缓存
     */
    public void delete(String key) {
        try {
            redisTemplate.delete(key);
            log.debug("Cache deleted: {}", key);
        } catch (Exception e) {
            log.error("Failed to delete cache: {}", key, e);
        }
    }

    /**
     * 删除多个缓存
     */
    public void delete(String... keys) {
        try {
            for (String key : keys) {
                redisTemplate.delete(key);
            }
            log.debug("Caches deleted: {} keys", keys.length);
        } catch (Exception e) {
            log.error("Failed to delete caches", e);
        }
    }

    /**
     * 检查缓存是否存在
     */
    public boolean hasKey(String key) {
        try {
            Boolean exists = redisTemplate.hasKey(key);
            return exists != null && exists;
        } catch (Exception e) {
            log.error("Failed to check cache existence: {}", key, e);
            return false;
        }
    }

    /**
     * 设置缓存过期时间
     */
    public void expire(String key, long timeout, TimeUnit unit) {
        try {
            redisTemplate.expire(key, timeout, unit);
            log.debug("Cache expiration set: {} ({})", key, timeout);
        } catch (Exception e) {
            log.error("Failed to set cache expiration: {}", key, e);
        }
    }

    /**
     * 获取缓存过期时间
     */
    public long getExpire(String key, TimeUnit unit) {
        try {
            Long expire = redisTemplate.getExpire(key, unit);
            return expire != null ? expire : -1;
        } catch (Exception e) {
            log.error("Failed to get cache expiration: {}", key, e);
            return -1;
        }
    }

    /**
     * 清空所有缓存
     */
    public void flushAll() {
        try {
            redisTemplate.getConnectionFactory().getConnection().flushAll();
            log.info("All caches flushed");
        } catch (Exception e) {
            log.error("Failed to flush all caches", e);
        }
    }
}
