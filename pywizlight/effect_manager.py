from dataclasses import dataclass
from typing import List, Optional, Union
from enum import IntEnum

class RenderingType(IntEnum):
    """Rendering type for effect steps."""
    RGB = 0
    KELVIN = 1
    
class ModifierType(IntEnum):
    """Modifier types for effects."""
    ELM_MDF_STATIC = 0
    ELM_MDF_CYCLE = 1
    ELM_MDF_PROGRESSIVE = 2
    ELM_MDF_RANDOM = 3
    ELM_MDF_MH_STATIC = 100
    ELM_MDF_MH_FLOW = 101
    ELM_MDF_MH_SPARKLE = 102
    ELM_MDF_MH_RANDOM = 103
    ELM_MDF_MH_FLYIN = 104
    ELM_MDF_MH_TWINKLE = 105

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
    rand: int = 0 # 0 - 100 different seeds for randomness
    advanced: int = 0 # takes 0 or 1
    software_head: int = 0 # manages the queue of effects
    
    def __post_init__(self):
        """Validate step parameters."""
        self._validate_rgb_values()
        self._validate_dimming()
        self._validate_duration()
    
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
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, duration: int = 1000, dimming: int = 100, **kwargs) -> 'EffectStep':
        """Create an RGB step."""
        return cls(
            rendering_type=RenderingType.RGB,
            r=r, g=g, b=b,
            duration=duration,
            dimming=dimming,
            **kwargs
        )
    
    @classmethod
    def from_kelvin(cls, cct: int, duration: int = 1000, dimming: int = 100, **kwargs) -> 'EffectStep':
        """Create a Kelvin temperature step."""
        return cls(
            rendering_type=RenderingType.KELVIN,
            cct=cct,
            duration=duration,
            dimming=dimming,
            **kwargs
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
    modifier: ModifierType = ModifierType.ELM_MDF_MH_SPARKLE
    gradient: bool = True
    init_step: int = 0
    rand: int = 0
    duration: int = 10  # seconds
    
    def __post_init__(self):
        """Validate effect details."""
        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
        if not 0 <= self.init_step:
            raise ValueError(f"init_step must be non-negative, got {self.init_step}")

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
                        "modifier": self.details.modifier,
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
    
    @classmethod
    def rainbow_fade(cls, duration: int = 10, step_duration: int = 1000) -> 'PreviewEffect':
        """Create a rainbow fade effect."""
        steps = [
            EffectStep.from_rgb(255, 0, 0, step_duration),    # Red
            EffectStep.from_rgb(255, 127, 0, step_duration),  # Orange
            EffectStep.from_rgb(255, 255, 0, step_duration),  # Yellow
            EffectStep.from_rgb(0, 255, 0, step_duration),    # Green
            EffectStep.from_rgb(0, 0, 255, step_duration),    # Blue
            EffectStep.from_rgb(75, 0, 130, step_duration),   # Indigo
            EffectStep.from_rgb(148, 0, 211, step_duration),  # Violet
        ]
        details = EffectDetails(duration=duration)
        return cls(details, steps)
    
    @classmethod
    def breathing_white(cls, duration: int = 10) -> 'PreviewEffect':
        """Create a breathing white effect."""
        steps = [
            EffectStep.from_kelvin(3000, 1000, 10),   # Dim warm white
            EffectStep.from_kelvin(3000, 1000, 100),  # Bright warm white
        ]
        details = EffectDetails(duration=duration)
        return cls(details, steps)
