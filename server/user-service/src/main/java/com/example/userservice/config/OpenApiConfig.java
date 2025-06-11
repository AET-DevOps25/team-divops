package com.example.userservice.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.*;
import org.springframework.context.annotation.Configuration;

/** Swagger-UI: http://localhost:8081/swagger-ui.html */
@Configuration
@OpenAPIDefinition(
        info = @Info(title = "User Service (internal)", version = "v1"),
        security = @SecurityRequirement(name = "BasicAuth")
)
@SecurityScheme(
        name = "BasicAuth",
        type = SecuritySchemeType.HTTP,
        scheme = "basic"
)
public class OpenApiConfig {}