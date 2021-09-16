from pyfra import *

@force_run()
def make_tpu_vm(rem_gcp, tpu_name, zone="europe-west4-a", type="v3-8"):
    user = rem_gcp.sh("echo $USER").strip()

    def _get_tpu_ssh():
        ip = rem_gcp.sh(f"gcloud alpha compute tpus tpu-vm describe {tpu_name} --format='get(networkEndpoints[0].accessConfig.externalIp)'".strip())
        return Remote(f"{user}@{ip}")
    
    try:
        r = _get_tpu_ssh()
        r.sh("echo hello from tpu")
        return r
    except ShellException:
        pass

    rem_gcp.sh(f"""
    echo y | gcloud alpha compute tpus tpu-vm delete {tpu_name}
    gcloud alpha compute tpus tpu-vm create {tpu_name} \
        --zone={zone} \
        --accelerator-type={type} \
        --version=v2-alpha 
    gcloud alpha compute tpus tpu-vm ssh {tpu_name} --zone {zone} --command="echo $(cat {local.path("~/.ssh/id_rsa.pub")}) >> ~/.ssh/authorized_keys"
    """)

    time.sleep(10)

    return _get_tpu_ssh()

def train_jax_pod(rem_gcp, tpu_name, tpu_size, run_name, dataset_name, dataset_bucket, model_bucket, val_name, zone="europe-west4-a", type="v3-256"):
    e = rem_gcp.env(f"mtj_{run_name}", "https://github.com/kingoflolz/mesh-transformer-jax")
    rem_gcp.sh(f"""
    gcloud alpha compute tpus tpu-vm create {tpu_name} \
        --zone={zone} \
        --accelerator-type={type} \
        --version=v2-alpha \
        --preemptible
    """)
    e.sh(f"""
    # pip install --upgrade jaxlib==0.1.67 jax==0.2.12 ray[default]==1.4.1 fabric dataclasses optax git+https://github.com/deepmind/dm-haiku tqdm cloudpickle smart_open[gcs] einops func_timeout
    gsutil ls "gs://{dataset_bucket}/{dataset_name}" > data/{dataset_name}.train.index
    gsutil ls "gs://{dataset_bucket}/{val_name}" > data/{dataset_name}.val.index
    wandb login
    """)
    e.path(f"configs/{run_name}.json").jwrite({
        "layers": 64,
        "d_model": 6144,
        "n_heads": 24,
        "n_vocab": 50400,
        "norm": "layernorm",
        "pe": "rotary",
        "pe_rotary_dims": 64,

        "seq": 2048,
        "cores_per_replica": 8,
        "per_replica_batch": 1,
        "gradient_accumulation_steps": 16,

        "warmup_steps": 3000,
        "anneal_steps": 300000,
        "lr": 1.0e-4,
        "end_lr": 1.0e-5,
        "weight_decay": 0.1,
        "total_steps": 350000,

        "tpu_size": tpu_size,

        "bucket": model_bucket,
        "model_dir": run_name,

        "train_set": f"{dataset_name}.train.index",
        "val_set": {
            "val": f"{dataset_name}.val.index"
        },

        "eval_harness_tasks": [
            "lambada",
            "piqa",
            "hellaswag",
            "winogrande",
            "mathqa",
            "pubmedqa"
        ],

        "val_batches": 100,
        "val_every": 500,
        "ckpt_every": 500,
        "keep_every": 10000,

        "name": run_name,
        "comment": ""
    })
    e.sh(f"""
    python3 train.py --config=configs/{run_name}.json --tpu {tpu_name}
    """)
    # e.sh("python3 slim_model.py --config=configs/carp.json")