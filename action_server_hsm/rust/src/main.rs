use zenoh::prelude::r#async::*;

#[async_std::main]
async fn main() {
    println!("Action Server");

    let session = zenoh::open(config::default()).res().await.unwrap();

    let key_expression = "Genotyper/1/DNASensor/1".to_string();
    let status_key = format!("{}/status", key_expression);
    println!("status_key: {}", status_key);

    loop {
        session.put(&status_key, "idle").res().await.unwrap();
    }

    session.close().res().await.unwrap();
}
