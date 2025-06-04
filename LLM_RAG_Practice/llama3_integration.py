"""
Basic Llama model integration and text generation.

This module demonstrates how to:
1. Load and initialize a Llama model
2. Generate text with different parameters
3. Handle context management
4. Implement basic error handling
"""

import os
from typing import List, Optional
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    BitsAndBytesConfig
)

class LlamaIntegration:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ):
        """
        Initialize the Llama model integration.

        Args:
            model_name: Name of the model to load
            device: Device to run the model on
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
        """
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p

        # Configure quantization for efficient inference
        self.quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=self.quantization_config,
            device_map="auto",
        )

        # Create text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto",
        )

    def generate_text(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Generate text based on the input prompt.

        Args:
            prompt: Input text to generate from
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter

        Returns:
            Generated text
        """
        try:
            # Use provided parameters or defaults
            max_new_tokens = max_new_tokens or self.max_length
            temperature = temperature or self.temperature
            top_p = top_p or self.top_p

            # Generate text
            outputs = self.generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            return outputs[0]["generated_text"]

        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return ""

    def generate_with_context(
        self,
        prompt: str,
        context: List[str],
        max_new_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text with additional context.

        Args:
            prompt: Input text to generate from
            context: List of context strings
            max_new_tokens: Maximum number of tokens to generate

        Returns:
            Generated text
        """
        # Combine context and prompt
        full_prompt = "\n".join(context) + "\n" + prompt
        return self.generate_text(full_prompt, max_new_tokens)

def main():
    """Example usage of the LlamaIntegration class."""
    # Initialize the model
    llama = LlamaIntegration()

    # Example 1: Basic text generation
    prompt = "Explain the concept of RAG (Retrieval-Augmented Generation) in simple terms."
    response = llama.generate_text(prompt)
    print("Basic Generation:")
    print(response)
    print("\n" + "="*50 + "\n")

    # Example 2: Generation with context
    context = [
        "RAG combines retrieval-based and generation-based approaches.",
        "It uses external knowledge to improve LLM responses.",
    ]
    response = llama.generate_with_context(prompt, context)
    print("Generation with Context:")
    print(response)

if __name__ == "__main__":
    main() 