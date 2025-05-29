package com.example.hackathon.Exceptions;

import org.springframework.dao.DataIntegrityViolationException;

public class UniqueConstraintException extends DataIntegrityViolationException {
    public UniqueConstraintException(String message) {
        super(message);
    }
}
