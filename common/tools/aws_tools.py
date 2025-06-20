"""
Herramientas personalizadas para interactuar con AWS.
"""
from strands import tool
import boto3
import json

@tool
def list_aws_resources(service: str, resource_type: str, region: str = "us-west-2") -> str:
    """
    Lista recursos AWS de un tipo específico.
    
    Args:
        service (str): Servicio AWS (ej. "ec2", "s3", "lambda")
        resource_type (str): Tipo de recurso a listar (ej. "instances", "buckets", "functions")
        region (str): Región AWS (por defecto "us-west-2")
        
    Returns:
        str: Lista de recursos en formato JSON
    """
    try:
        session = boto3.Session(region_name=region)
        client = session.client(service)
        
        # Mapeo de servicios y métodos para listar recursos
        resource_methods = {
            "ec2": {
                "instances": "describe_instances",
                "security_groups": "describe_security_groups",
                "vpcs": "describe_vpcs",
                "subnets": "describe_subnets"
            },
            "s3": {
                "buckets": "list_buckets"
            },
            "lambda": {
                "functions": "list_functions"
            },
            "rds": {
                "instances": "describe_db_instances"
            }
        }
        
        if service not in resource_methods or resource_type not in resource_methods[service]:
            return f"Error: Combinación de servicio '{service}' y tipo de recurso '{resource_type}' no soportada."
        
        method_name = resource_methods[service][resource_type]
        method = getattr(client, method_name)
        response = method()
        
        # Simplificar la respuesta para hacerla más legible
        simplified = {"resources": []}
        
        if service == "ec2" and resource_type == "instances":
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    simplified["resources"].append({
                        "id": instance.get("InstanceId"),
                        "type": instance.get("InstanceType"),
                        "state": instance.get("State", {}).get("Name"),
                        "private_ip": instance.get("PrivateIpAddress", "N/A"),
                        "public_ip": instance.get("PublicIpAddress", "N/A")
                    })
        elif service == "s3" and resource_type == "buckets":
            for bucket in response.get("Buckets", []):
                simplified["resources"].append({
                    "name": bucket.get("Name"),
                    "creation_date": bucket.get("CreationDate").isoformat() if bucket.get("CreationDate") else "N/A"
                })
        else:
            # Respuesta genérica para otros tipos de recursos
            simplified = response
        
        return json.dumps(simplified, indent=2, default=str)
    except Exception as e:
        return f"Error al listar recursos: {str(e)}"

@tool
def analyze_aws_costs(service: str = None, period: str = "MONTHLY", region: str = "us-west-2") -> str:
    """
    Analiza los costos de AWS para un servicio específico o todos los servicios.
    
    Args:
        service (str, optional): Servicio AWS específico (ej. "EC2", "S3")
        period (str): Período de tiempo ("DAILY", "WEEKLY", "MONTHLY")
        region (str): Región AWS (por defecto "us-west-2")
        
    Returns:
        str: Análisis de costos en formato JSON
    """
    try:
        session = boto3.Session(region_name=region)
        client = session.client('ce')  # Cost Explorer
        
        # Configurar el período de tiempo
        import datetime
        end = datetime.datetime.now()
        
        if period == "DAILY":
            start = end - datetime.timedelta(days=1)
            granularity = "HOURLY"
        elif period == "WEEKLY":
            start = end - datetime.timedelta(days=7)
            granularity = "DAILY"
        else:  # MONTHLY
            start = end - datetime.timedelta(days=30)
            granularity = "DAILY"
        
        # Formatear fechas para la API
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        # Configurar filtros
        filters = {}
        if service:
            filters = {
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": [service]
                }
            }
        
        # Hacer la solicitud a Cost Explorer
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_str,
                'End': end_str
            },
            Granularity=granularity,
            Metrics=['BlendedCost', 'UsageQuantity'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ],
            Filter=filters if service else {}
        )
        
        return json.dumps(response, indent=2, default=str)
    except Exception as e:
        return f"Error al analizar costos: {str(e)}"
