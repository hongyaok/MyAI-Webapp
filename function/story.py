from diffusers import DiffusionPipeline
import torch
from compel import Compel, ReturnedEmbeddingsType
from diffusers import DiffusionPipeline, AutoencoderKL
from PIL import Image
from datetime import datetime
from tqdm.auto import tqdm
import os
from random import randint, choice
import string


def prompt_story(prompt, no, to):
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix",
                                        torch_dtype=torch.float16)
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        vae=vae,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True
    )

    base.load_lora_weights("blink7630/storyboard-sketch")

    _ = base.to("cuda")
    # base.enable_model_cpu_offload()  # recommended for T4 GPU if enough system RAM

    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )

    _ = refiner.to("cuda")

    compel_base = Compel(tokenizer=[base.tokenizer, base.tokenizer_2] , text_encoder=[base.text_encoder, base.text_encoder_2], returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, requires_pooled=[False, True])
    compel_refiner = Compel(tokenizer=refiner.tokenizer_2 , text_encoder=refiner.text_encoder_2, returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, requires_pooled=True)

    high_noise_frac = 0.8

    def gen_image(source_prompt, no, to ,cfg=13, seed=-1, webp_output=True):
        if seed < 0:
            seed = randint(0, 10**8)
            print(f"Seed: {seed}")

        prompt = source_prompt
        negative_prompt = "wrong"  # hardcoding

        conditioning, pooled = compel_base(prompt)
        conditioning_neg, pooled_neg = compel_base(negative_prompt) if negative_prompt is not None else (None, None)
        generator = torch.Generator(device="cuda").manual_seed(seed)

        latents = base(prompt_embeds=conditioning,
                    pooled_prompt_embeds=pooled,
                    negative_prompt_embeds=conditioning_neg,
                    negative_pooled_prompt_embeds=pooled_neg,
                    guidance_scale=cfg,
                    denoising_end=high_noise_frac,
                    generator=generator,
                    output_type="latent",
                    cross_attention_kwargs={"scale": 1.}
                    ).images

        conditioning, pooled = compel_refiner(prompt)
        conditioning_neg, pooled_neg = compel_refiner(negative_prompt) if negative_prompt is not None else (None, None)
        generator = torch.Generator(device="cuda").manual_seed(seed)

        images = refiner(
            prompt_embeds=conditioning,
            pooled_prompt_embeds=pooled,
            negative_prompt_embeds=conditioning_neg,
            negative_pooled_prompt_embeds=pooled_neg,
            guidance_scale=cfg,
            denoising_start=high_noise_frac,
            image=latents,
            generator=generator,
            ).images

        image = images[0]

        webp_output = True
        if webp_output:
            fname = to+"/"+''.join(choice(string.ascii_letters) for x in range(4)) +".png"
            image.save(fname) #format="webp")
            return fname
        else:
            image.save(f"img{no}.png")

    return gen_image(prompt, no, to)
   

#For testing
if __name__ == "__main__":
    prompt = input("Enter the text you want to convert to image: ")
    prompt_story(prompt, 0, "../uploads")