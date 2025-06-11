package com.example.gateway.client;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class UserServiceClient {

    private final WebClient web;

    public UserServiceClient(@Value("${user-service.base-url}") String baseUrl,
                             WebClient.Builder builder) {
        this.web = builder.baseUrl(baseUrl).build();
    }

    public void register(Map<String, String> dto) {
        web.post().uri("/internal/users").bodyValue(dto).retrieve().toBodilessEntity().block();
    }

    public boolean verify(String email, String pwd) {
        return web.post().uri("/internal/auth/verify")
                .bodyValue(Map.of("email", email, "password", pwd))
                .retrieve().toBodilessEntity()
                .map(r -> r.getStatusCode().is2xxSuccessful()).block();
    }

    public Map<String, Object> find(String email) {
        return web.get().uri("/internal/users/{email}", email)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {
                })
                .block();
    }
}
