package com.example.hackathon.Usuario.domain;

import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Usuario.infrastructure.UsuarioRepository;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UsuarioService implements UserDetailsService {
    @Autowired
    private UsuarioRepository<Usuario> usuarioRepository;

    @Autowired
    private ModelMapper modelMapper;

    public UserDetailsService userDetailsService() {
        return username -> {
            Optional<Usuario> usuario = usuarioRepository.findByEmail(username);
            if (usuario.isEmpty()) new UsernameNotFoundException("User not found");
            return (UserDetails) usuario.get();
        };
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return (Usuario) usuarioRepository.findByEmail(username).get();
    }

}
