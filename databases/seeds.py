import secrets
from helpers.loog import logger
from helpers.config import AppConfig
from databases.models import RoleModel, UserModel, ToolModel, LLMModel, AgentModel
from sqlalchemy.future import select
from passlib.context import CryptContext
from bedrock.factory import PromptFactory

app_conf = AppConfig()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def seed_role(session):
    """Initialize default role."""
    result = await session.execute(select(RoleModel))
    existing_roles = result.scalars().all()

    if not existing_roles:
        roles = [
            RoleModel(name="administrator", description="Administrator with full access"),
            RoleModel(name="maintainer", description="Maintainer role with elevated permissions"),
            RoleModel(name="enduser", description="Standard user with limited permissions"),
        ]
        session.add_all(roles)
        await session.commit()
        logger.info("✅ Roles initialized")

async def seed_admin(session):
    """Initialize default admin user."""
    result = await session.execute(select(UserModel).where(UserModel.username == "administrator"))
    admin = result.scalars().first()

    if admin:
        logger.info("👤 Default admin user already exists.")
        return

    # Get admin role
    sql_role = await session.execute(select(RoleModel).where(RoleModel.name == "admin"))
    admin_role = sql_role.scalars().first()
    
    init_admin_password = secrets.token_hex(16)

    admin_user = UserModel(
        username="administrator",
        email=app_conf.app_admin_email,
        hashed_password=pwd_context.hash(init_admin_password),
        fullname="Administrator",
        role_id=admin_role.id
    )

    session.add(admin_user)
    await session.commit()
    logger.info(f"✅ Created default admin user: {app_conf.app_admin_email}")
    logger.info(f"✅ Created default admin password: {init_admin_password}")

async def seed_tool(session):
    tools = [
        {"name": "duckduckgo", "display_name": "DuckDuckGo", "status": "disable", "logo": "🦆", "description": "Privacy-focused general-purpose web search.", "tags": ["Search", "Web", "Private"]},
        {"name": "arxiv", "display_name": "Arxiv", "status": "disable", "logo": "📚", "description": "Search academic papers and preprints from arXiv.", "tags": ["Research", "Academic"]},
        {"name": "wikipedia", "display_name": "Wikipedia", "status": "disable", "logo": "📖", "description": "Retrieve general knowledge, summaries, and definitions.", "tags": ["Knowledge", "Reference"]},
        {"name": "google_search", "display_name": "GoogleSearch", "status": "disable", "logo": "🌐", "description": "Comprehensive Google-powered web search.", "tags": ["Search", "Web", "Public"]},
        {"name": "google_scholar", "display_name": "GoogleScholar", "status": "disable", "logo": "🎓", "description": "Search scholarly publications and citations.", "tags": ["Research", "Academic"]},
        {"name": "google_trends", "display_name": "GoogleTrends", "status": "disable", "logo": "📈", "description": "Analyze trending search queries and interest over time.", "tags": ["Analytics", "Search"]},
        {"name": "asknews", "display_name": "AskNews", "status": "disable", "logo": "🗞️", "description": "Fetch the latest breaking news from various sources.", "tags": ["News", "Trending"]},
        {"name": "reddit", "display_name": "RedditSearch", "status": "disable", "logo": "💬", "description": "Find community discussions and opinions from Reddit.", "tags": ["Community", "Social"]},
        {"name": "searx", "display_name": "SearxSearch", "status": "disable", "logo": "🕸️", "description": "Meta search engine combining results from multiple sources.", "tags": ["Search", "Meta"]},
        {"name": "openweather", "display_name": "OpenWeather", "status": "disable", "logo": "⛅", "description": "Check current and forecasted weather conditions.", "tags": ["Utility", "Environment"]},
    ]

    for t in tools:
        result = await session.execute(select(ToolModel).where(ToolModel.name == t["name"]))
        existing = result.scalars().first()
        if not existing:
            session.add(ToolModel(**t))

    await session.commit()
    logger.info("✅ Tools seeded successfully")

async def seed_llm(session):
    """Initialize default llm."""
    result = await session.execute(select(LLMModel))
    existing_llms = result.scalars().all()

    if not existing_llms:
        llms = [
            LLMModel(
                name="anthropic_claude_sonet_4_5",
                display_name="Claude Sonet 4.5",
                description="Anthropic Claude Sonet 4.5 LLM hosted on AWS Bedrock",
                logo="anthropic.png",
                provider="Anthropic via AWS Bedrock",
                region="us-east-1",
                model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                model_max_tokens="4096",
                model_temperature="0.7",
                system_prompt=PromptFactory.load_llm_prompt()
            ),
            LLMModel(
                name="gpt_oss_120b",
                display_name="GPT-OSS 120B",
                description="GPT OSS models are open-source large language models hosted on AWS Bedrock.",
                logo="openai.png",
                provider="OpenAI via AWS Bedrock",
                region="us-east-1",
                model_id="openai.gpt-oss-120b-1:0",
                model_max_tokens="4096",
                model_temperature="0.7",
                system_prompt=PromptFactory.load_llm_prompt()
            ),
            LLMModel(
                name="llama_4_scout_17b_instruct",
                display_name="Llama 4 Scout 17B Instruct",
                description="Meta Llama 4 Scout 17B Instruct model hosted on AWS Bedrock.",
                logo="meta.png",
                provider="Meta via AWS Bedrock",
                region="us-east-1",
                model_id="us.meta.llama4-scout-17b-instruct-v1:0",
                model_max_tokens="4096",
                model_temperature="0.7",
                system_prompt=PromptFactory.load_llm_prompt()
            )
        ]
        session.add_all(llms)
        await session.commit()
        logger.info("✅ LLMs seeded successfully")

async def seed_agent(session):
    """Initialize default agent."""
    result = await session.execute(select(AgentModel))
    existing_agents = result.scalars().all()

    if not existing_agents:
        # Get first LLM
        sql_all_llms = await session.execute(select(LLMModel))
        all_llms = sql_all_llms.scalars().all()
        llm_ids = [{"id": l.id, "name": l.name} for l in all_llms]

        # Get enabled tools
        sql_tools = await session.execute(
            select(ToolModel).where(ToolModel.status == "enable")
        )
        enabled_tools = sql_tools.scalars().all()

        # Convert tools → [{"id":1,"name":"duckduckgo"}, ...]
        tool_list = [{"id": t.id, "name": t.name} for t in enabled_tools]

        agent = AgentModel(
            name="yang-agent",
            display_name="YangYang",
            description="YangYang is a general-purpose agent that can use the tools provided to perform tasks.",
            logo="yang.png",
            tags=["general", "agent"],
            llm_ids=llm_ids,
            system_prompt=PromptFactory.load_agent_prompt(),
            tools=tool_list,
            default_agent=True,
        )

        session.add(agent)
        await session.commit()
        logger.info("✅ Agents seeded successfully")

async def seed_initial_data(session):
    await seed_role(session)
    await seed_admin(session)
    await seed_tool(session)
    await seed_llm(session)
    await seed_agent(session)