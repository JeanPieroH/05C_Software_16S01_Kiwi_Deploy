package com.example.hackathon.Email.event;

import com.example.hackathon.Email.domain.Email;
import org.springframework.context.ApplicationEvent;

public class EmailEvent extends ApplicationEvent {
    private Email mail;

    public EmailEvent(Email mail) {
        super(mail);
        this.mail = mail;
    }

    public Email getEmail() {
        return mail;
    }
}
