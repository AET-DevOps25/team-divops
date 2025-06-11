package com.example.userservice.service;

import com.example.userservice.model.User;
import com.example.userservice.repository.UserRepository;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class UserService {

    private final UserRepository repo;
    private final PasswordEncoder encoder = new BCryptPasswordEncoder();

    public void register(Map<String, String> d) {
        repo.save(new User(d.get("email"),
                d.get("firstName"),
                d.get("lastName"),
                LocalDate.parse(d.get("birthdate")),
                encoder.encode(d.get("password")),
                "USER", true));
    }

    public boolean verify(String email, String raw) {
        return repo.findByEmail(email)
                .filter(u -> encoder.matches(raw, u.getPassword()))
                .isPresent();
    }

    public Map<String, Object> find(String email) {
        return repo.findByEmail(email)
                .map(u -> Map.<String, Object>of("email", u.getEmail(),
                        "firstName", u.getFirstName(),
                        "lastName", u.getLastName(),
                        "birthdate", u.getBirthdate()))
                .orElseThrow();
    }
}
