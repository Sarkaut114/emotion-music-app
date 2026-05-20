package com.emotion.music.controller;

import java.util.Map;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.client.RestTemplate;

@Controller
public class AppController {
    
    @GetMapping("/")
    public String home(Model model) {
        
        String flaskUrl = "http://localhost:5000/emotion";
        RestTemplate restTemplate = new RestTemplate();
        Map response = restTemplate.getForObject(flaskUrl, Map.class);
        String emotion = (String) response.get("emotion");
        model.addAttribute("emotion", emotion);
        
        return "index";
    }
}
