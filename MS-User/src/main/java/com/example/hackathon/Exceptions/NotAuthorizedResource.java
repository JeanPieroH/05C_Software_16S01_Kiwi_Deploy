package com.example.hackathon.Exceptions;

public class NotAuthorizedResource extends RuntimeException{
    public NotAuthorizedResource(String message) {
        super(message);
    }
}
