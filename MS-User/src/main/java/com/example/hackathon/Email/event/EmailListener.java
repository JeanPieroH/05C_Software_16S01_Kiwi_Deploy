package com.example.hackathon.Email.event;

import com.example.hackathon.Email.domain.EmailService;
import jakarta.mail.MessagingException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class EmailListener {
    @Autowired
    private EmailService emailService;

    @EventListener
    @Async
    public void handleEmailEvent(EmailEvent event) throws MessagingException, IOException {
        emailService.sendEmail(event.getEmail());
    }
}
