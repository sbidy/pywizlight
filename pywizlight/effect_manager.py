from dataclasses import dataclass
from typing import List
from enum import IntEnum

class RenderingType(IntEnum):
    """Rendering type for effect steps."""
    RGB = 0 
    KELVIN = 1
    
# More modifiers will be added
class ModifierType(IntEnum):
    """Modifier types for effects."""
    
    # Each color will play the same color in all software heads (Used for lightbulbs mostly, if used on multiple software heads, all will play the same color)
    ELM_MDF_STATIC = 0 
    ELM_MDF_CYCLE = 1
    ELM_MDF_PROGRESSIVE = 2
    ELM_MDF_RANDOM = 3
    
    # Different colors in each software head (Used for LED Strips and other devices with multiple LEDs)
    ELM_MDF_MH_STATIC = 100 
    ELM_MDF_MH_FLOW = 101 
    ELM_MDF_MH_SPARKLE = 102 # Sparkle effect
    ELM_MDF_MH_RANDOM = 103 # Each software head will change color randomly based on the light mode definition
    ELM_MDF_MH_FLYIN = 104 # Flyin effect
    ELM_MDF_MH_TWINKLE = 105 # Twinkle effect

MAX_EFFECT_STEPS = 12 # Max number of steps that bulbs accept 

# SUBJECT TO CHANGE params: rand and advanced (not in use yet)
@dataclass
class EffectStep:
    """Represents a single step in a preview effect."""
    rendering_type: RenderingType = RenderingType.RGB
    r: int = 0
    g: int = 0
    b: int = 0
    ww: int = 0  # warm white
    cw: int = 0  # cold white
    cct: int = 0  # kelvin temperature from 0 - 12000
    dimming: int = 100  # 0-100 brightness power
    duration: int = 1000  # milliseconds
    transition: int = 0
    # NOT IN USE YET
    rand: int = 0 # 0 - 100 different seeds for randomness
    # NOT IN USE YET
    advanced: int = 0 # takes 0 or 1 
    software_head: int = 0 # manages the order of lights on each software head. 0 is the first LED of LED strip, 1 is the second LED, etc.
    
    def __post_init__(self):
        """Validate step parameters."""
        self._validate_rgb_values()
        self._validate_dimming()
        self._validate_duration()
        self._validate_cct()
        self._validate_rand()
        self._validate_advanced()
    
    def _validate_rgb_values(self):
        """Validate RGB values are in valid range."""
        for color, value in [('r', self.r), ('g', self.g), ('b', self.b)]:
            if not 0 <= value <= 255:
                raise ValueError(f"{color} value must be between 0-255, got {value}")
    
    def _validate_dimming(self):
        """Validate dimming value."""
        if not 0 <= self.dimming <= 100:
            raise ValueError(f"Dimming must be between 0-100, got {self.dimming}")
    
    def _validate_duration(self):
        """Validate duration value."""
        if self.duration < 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
    
    def _validate_cct(self):
        """Validate CCT (color temperature) value."""
        if not 0 <= self.cct <= 12000:
            raise ValueError(f"CCT must be between 0-12000, got {self.cct}")
    
    def _validate_rand(self):
        """Validate rand value."""
        if not 0 <= self.rand <= 100:
            raise ValueError(f"Rand must be between 0-100, got {self.rand}")
    
    def _validate_advanced(self):
        """Validate advanced value."""
        if self.advanced not in (0, 1):
            raise ValueError(f"Advanced must be 0 or 1, got {self.advanced}")
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, ww: int = 0, cw: int = 0, duration: int = 1000, dimming: int = 100, transition: int = 100, software_head: int = 0) -> 'EffectStep':
        """Create an RGB step."""
        return cls(
            rendering_type=RenderingType.RGB,
            r=r, g=g, b=b,
            ww=ww, cw=cw,
            duration=duration,
            dimming=dimming,
            transition=transition,
            software_head=software_head
        )
    
    @classmethod
    def from_kelvin(cls, cct: int, duration: int = 1000, dimming: int = 100, transition: int = 100, software_head: int = 0) -> 'EffectStep':
        """Create a Kelvin temperature step."""
        return cls(
            rendering_type=RenderingType.KELVIN,
            cct=cct,
            duration=duration,
            dimming=dimming,
            transition=transition,
            software_head=software_head
        )
    
    def to_array(self) -> List[int]:
        """Convert step to array format expected by the bulb."""
        return [
            self.rendering_type.value,
            self.r, self.g, self.b,
            self.ww, self.cw, self.cct,
            self.dimming, self.duration, self.transition,
            self.rand, self.advanced, self.software_head
        ]

@dataclass
class EffectDetails:
    """Configuration details for a preview effect."""
    modifier: ModifierType = ModifierType.ELM_MDF_STATIC
    gradient: bool = True
    init_step: int = 0 # Which step will play on the first LED (software head). For lightbulbs, set to 0 by default.
    rand: int = 0
    duration: int = 10  # seconds
    
    def __post_init__(self):
        """Validate effect details."""
        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
        if not 0 <= self.init_step:
            raise ValueError(f"init_step must be non-negative, got {self.init_step}")
        if not 0 <= self.rand <= 100:
            raise ValueError(f"rand must be between 0-100, got {self.rand}")

class PreviewEffect:
    """Manages a complete preview effect with details and steps."""
    
    def __init__(self, details: EffectDetails, steps: List[EffectStep]):
        self.details = details
        self.steps = steps
        self._validate_steps()
    
    def _validate_steps(self):
        """Validate that steps are compatible with effect details."""
        if not self.steps:
            raise ValueError("Effect must have at least one step")
        
        if len(self.steps) > MAX_EFFECT_STEPS:
            raise ValueError(f"Effect cannot have more than {MAX_EFFECT_STEPS} steps, got {len(self.steps)}")
        
        if self.details.init_step >= len(self.steps):
            raise ValueError(f"init_step ({self.details.init_step}) must be less than number of steps ({len(self.steps)})")
    
    def calculate_total_duration(self) -> float:
        """Calculate total effect duration in seconds."""
        step_duration = sum(step.duration for step in self.steps) / 1000.0
        return max(step_duration, self.details.duration)
    
    def to_message(self) -> dict:
        """Convert to the message format expected by the bulb."""
        return {
            "method": "setEffect",
            "params": {
                "preview": {
                    "elm": {
                        "modifier": self.details.modifier.value,
                        "gradient": self.details.gradient,
                        "initStep": self.details.init_step,
                        "rand": self.details.rand,
                        "steps": [step.to_array() for step in self.steps]
                    },
                    "state": True,
                    "duration": self.details.duration,
                }
            }
        }
    
    # Class methods to test effect or gain insight
    @classmethod
    def rainbow_fade(cls, duration: int = 10, step_duration: int = 1000) -> 'PreviewEffect':
        """Create a rainbow fade effect with smooth transitions."""
        steps = [
            EffectStep.from_rgb(255, 0, 0, step_duration, transition=400),    # Red
            EffectStep.from_rgb(255, 127, 0, step_duration, transition=400),  # Orange
            EffectStep.from_rgb(255, 255, 0, step_duration, transition=400),  # Yellow
            EffectStep.from_rgb(0, 255, 0, step_duration, transition=400),    # Green
            EffectStep.from_rgb(0, 0, 255, step_duration, transition=400),    # Blue
            EffectStep.from_rgb(75, 0, 130, step_duration, transition=400),   # Indigo
            EffectStep.from_rgb(148, 0, 211, step_duration, transition=400),  # Violet
        ]
        details = EffectDetails(duration=duration)
        return cls(details, steps)

    @classmethod
    def breathing_white(cls, duration: int = 10) -> 'PreviewEffect':
        """Create a breathing white effect with smooth transitions."""
        steps = [
            EffectStep.from_kelvin(3000, 1000, 10, transition=500),   # Dim warm white - slow fade in
            EffectStep.from_kelvin(3000, 1000, 100, transition=500),  # Bright warm white - slow fade out
        ]
        details = EffectDetails(duration=duration)
        return cls(details, steps)