package com.a2s.backend.controller;

import com.a2s.backend.model.Design;
import com.a2s.backend.repository.DesignRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/gallery")
public class DesignController {

    @Autowired
    DesignRepository designRepository;

    @GetMapping
    public List<Design> getAllDesigns() {
        return designRepository.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Design> getDesignById(@PathVariable String id) {
        Optional<Design> design = designRepository.findById(id);
        return design.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Design createDesign(@RequestBody Design design) {
        return designRepository.save(design);
    }

    @GetMapping("/room/{roomType}")
    public List<Design> getDesignsByRoomType(@PathVariable String roomType) {
        return designRepository.findByRoomType(roomType);
    }

    @GetMapping("/style/{style}")
    public List<Design> getDesignsByStyle(@PathVariable String style) {
        return designRepository.findByStyle(style);
    }
}
