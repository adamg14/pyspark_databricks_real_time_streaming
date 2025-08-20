# https://registry.terraform.io/providers/confluentinc/confluent/latest/docs
terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.37"
    }
  }
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret
}

# environment
resource "confluent_environment" "dev" {
  display_name = "dev"
}

# Kafka Cluster
resource "confluent_kafka_cluster" "standard" {
  display_name = "purchase_events_cluster"
  availability = "SINGLE_ZONE"
  cloud        = "GCP"
  region       = "europe-west2"
  standard {}

  environment {
    id = confluent_environment.dev.id
  }
}

# Service Account 
resource "confluent_service_account" "producer" {
  display_name = "python_producer"
  description  = "Service account for Python producer"
}

# role binding - this gives the serive account the permission to create a topic within the created cluster
resource "confluent_role_binding" "producer_topic_access" {
    principal = "User:${confluent_service_account.producer.id}"
    role_name = "DeveloperManager"
    crn_pattern = "${confluent_kafka_cluster.standard.rbac_crn}/kafka=${confluent_kafka_cluster.standard.id}/topic=*"
}

# Kafka Topic
resource "confluent_kafka_topic" "purchase_events" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }

  topic_name       = "purchase_events"
  partitions_count = 1
  rest_endpoint    = confluent_kafka_cluster.standard.rest_endpoint

  credentials {
    key = confluent_api_key.producer_key.id
    secret = confluent_api_key.producer_key.secret
  }

  config = {
    "cleanup.policy" = "delete"
    # retain messages for 1 day
    "retention.ms" = "86400000"
  }
}

# Using the above service account to manage the Kafka Cluster
resource "confluent_api_key" "producer_key" {
  display_name = "python_producer_key"
  description  = "API Key for Python producer"

  owner {
    id          = confluent_service_account.producer.id
    api_version = confluent_service_account.producer.api_version
    kind        = confluent_service_account.producer.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.standard.id
    api_version = confluent_kafka_cluster.standard.api_version
    kind        = confluent_kafka_cluster.standard.kind

    environment {
        id = confluent_environment.dev.id
    }

  }

}

output "bootstrap_servers" {
  value = confluent_kafka_cluster.standard.bootstrap_endpoint
}

output "api_key" {
  value     = confluent_api_key.producer_key.id
  sensitive = true
}

output "api_secret" {
  value     = confluent_api_key.producer_key.secret
  sensitive = true
}

variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API Key"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API Key"
  type        = string
  sensitive   = true
}