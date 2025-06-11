package com.example.gateway.repository;

import com.example.gateway.model.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SessionRepository extends JpaRepository<Session, String> {

    Optional<Session> findByRefreshToken(String refreshToken);

    void deleteByEmail(String email);
}
