package com.example.hackathon.Teacher.application;

import java.security.Principal;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.hackathon.Teacher.domain.Teacher;
import com.example.hackathon.Teacher.domain.TeacherService;

@RestController
@RequestMapping("/teacher")
public class TeacherController {

    @Autowired
    TeacherService teacherService;

    @GetMapping("/me")
    public ResponseEntity<Teacher> getTeacher(Principal principal){
        return ResponseEntity.ok(teacherService.getTeacher(principal));
    }

    @PatchMapping("/me")
    public ResponseEntity<Teacher> patchTeacher(Principal principal,@RequestBody Teacher teacher){
        return ResponseEntity.ok(teacherService.patchTeacher(principal,teacher));
    }
    
}
