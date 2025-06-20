"""
Strands Agents Ecosystem - Multi-Agent Coordination System
=========================================================

A comprehensive system for coordinating specialized AI agents using the Strands framework.
This system demonstrates the "Agents as Tools" pattern for building sophisticated
multi-agent workflows.

Author: Open Source Community
License: MIT
"""
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents
from agents.coordinator.agent import coordinator_agent
from agents.aws_expert.agent import aws_expert_agent
from agents.networking.agent import networking_agent
from agents.cicd.agent import cicd_agent
from agents.iac.agent import iac_agent
from agents.kubernetes.agent import kubernetes_agent

# Import utilities
from common.utils.helpers import setup_logging
from common.utils.enhanced_callback import create_enhanced_callback
from common.utils.tool_interceptor import set_interception_enabled
from orchestrator.agent_graph import create_agent_graph, execute_workflow
from config.settings import LOG_LEVEL

def setup_agents_with_interception(enable_interception: bool = True):
    """
    Configure all agents with enhanced streaming and optional tool interception.
    
    Args:
        enable_interception: Whether to enable tool interception
    
    Returns:
        dict: Dictionary of configured agents
    """
    agents = {
        "coordinator": coordinator_agent,
        "aws_expert": aws_expert_agent,
        "networking": networking_agent,
        "cicd": cicd_agent,
        "iac": iac_agent,
        "kubernetes": kubernetes_agent
    }
    
    # Configure enhanced callback handler for all agents
    enhanced_callback = create_enhanced_callback(
        enable_interception=enable_interception,
        enable_streaming=True
    )
    
    for agent in agents.values():
        agent.callback_handler = enhanced_callback
    
    # Configure global interception
    set_interception_enabled(enable_interception)
    
    return agents

def show_welcome_message(interception_enabled: bool):
    """Display welcome message with system information."""
    print("=" * 70)
    print("🤖 STRANDS AGENTS ECOSYSTEM")
    print("   Multi-Agent Coordination System")
    print("=" * 70)
    print("Available Agents:")
    print("  • Coordinator - Orchestrates multi-agent workflows")
    print("  • AWS Expert - Cloud architecture and services")
    print("  • Networking Expert - VPC, subnets, and connectivity")
    print("  • CI/CD Expert - GitHub Actions and deployment pipelines")
    print("  • IaC Expert - Terraform and CloudFormation")
    print("  • Kubernetes Expert - Container orchestration and EKS")
    print()
    
    if interception_enabled:
        print("🔧 Tool Interception: ENABLED")
        print("   You'll be asked to confirm before agents use tools")
        print("   Options: [s]Yes [n]No [a]Approve all [t]Approve this type")
    else:
        print("🔧 Tool Interception: DISABLED")
        print("   Agents will use tools automatically")
    
    print()
    print("Commands:")
    print("  'intercept on/off' - Toggle tool interception")
    print("  'help' - Show this message")
    print("  'quit' - Exit the system")
    print("=" * 70)
    print()

def handle_special_commands(user_input: str) -> tuple[bool, bool]:
    """
    Handle special user commands.
    
    Returns:
        tuple: (is_special_command, should_continue)
    """
    command = user_input.lower().strip()
    
    if command in ["intercept on", "interception on"]:
        set_interception_enabled(True)
        print("✅ Tool interception ENABLED")
        return True, True
    elif command in ["intercept off", "interception off"]:
        set_interception_enabled(False)
        print("✅ Tool interception DISABLED")
        return True, True
    elif command in ["help", "h"]:
        show_welcome_message(True)  # Show help
        return True, True
    elif command in ["quit", "exit", "q"]:
        return True, False
    
    return False, True

def main():
    """Main application entry point."""
    # Setup logging
    setup_logging(LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    # Determine if tool interception should be enabled
    enable_interception = os.getenv("ENABLE_TOOL_INTERCEPTION", "true").lower() == "true"
    
    # Show welcome message
    show_welcome_message(enable_interception)
    
    # Setup agents with enhanced capabilities
    agents = setup_agents_with_interception(enable_interception)
    
    # Create agent graph using "Agents as Tools" pattern
    agent_graph = create_agent_graph(agents)
    logger.info(f"Agent graph created with {agent_graph.topology_type} topology")
    
    # Main interaction loop
    while True:
        try:
            user_query = input("Consulta: ")
            
            # Handle special commands
            is_special, should_continue = handle_special_commands(user_query)
            if is_special:
                if not should_continue:
                    print("\n👋 Thank you for using Strands Agents Ecosystem!")
                    break
                continue
            
            # Validate input
            if not user_query.strip():
                print("Please enter a valid query.")
                continue
            
            print("\n" + "="*60)
            print("🔄 Processing your query...")
            print("="*60)
            
            # Process query through agent graph
            execute_workflow(agent_graph, user_query)
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            break
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'help' for assistance.\n")

if __name__ == "__main__":
    main()
