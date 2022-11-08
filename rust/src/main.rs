use zenoh::prelude::r#async::*;

#[async_std::main]
async fn main() {
    println!("Action Server");

    let session = zenoh::open(config::default()).res().await.unwrap();

    let health_key = "Genotyper/1/DNASensor/1/health".to_string();
    loop {
        session.put(&health_key, "healthy").res().await.unwrap();
    }

    session.close().res().await.unwrap();
}
