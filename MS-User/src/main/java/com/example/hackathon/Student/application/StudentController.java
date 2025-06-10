package com.example.hackathon.Student.application;

import java.security.Principal;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Student.domain.StudentService;
import com.example.hackathon.Student.dto.RpStudentId;
import com.example.hackathon.Usuario.dto.RqListEmail;

import java.util.List;


@RestController
@RequestMapping("/student")
public class StudentController {
    @Autowired
    StudentService studentService;

    @GetMapping("/me")
    public ResponseEntity<Student> getStudent(Principal principal){
        return ResponseEntity.ok(studentService.getStudent(principal));
    }

    @PatchMapping("/me")
    public ResponseEntity<Student> patchStudent(Principal principal,@RequestBody Student student){
        return ResponseEntity.ok(studentService.patchStudent(principal,student));
    }

    @PostMapping("/by-ids")
    public ResponseEntity<List<Student>> getStudentsByIds(@RequestBody RpStudentId studentIds){
        if (studentIds == null || studentIds.getStudents_id().isEmpty()) {
            return ResponseEntity.badRequest().body(List.of());
        }

        List<Student> students = studentService.getStudentsByIds(studentIds.getStudents_id());
        return ResponseEntity.ok(students);
    }

    @PostMapping("/ids-by-email")
    public ResponseEntity<RpStudentId> getStudentsId(@RequestBody RqListEmail studentEmails){
        return ResponseEntity.ok(studentService.getStudentsIdsbyEmail(studentEmails));
    }

    @PostMapping("/{id}/add-coins/{points}")
    public ResponseEntity<Student> addCoins(@PathVariable("id") Long id,@PathVariable("points") int points) { 
        Student updatedStudent = studentService.addPoints(id, points);
        return ResponseEntity.ok(updatedStudent);
    }



}
