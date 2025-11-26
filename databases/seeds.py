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
            RoleModel(name="admin", description="Administrator with full access"),
            RoleModel(name="user", description="Standard user with limited permissions"),
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
        {"name": "duckduckgo", "status": "enable"},
        {"name": "arxiv", "status": "enable"},
        {"name": "wikipedia", "status": "enable"},
        {"name": "google_search", "status": "disable"},
        {"name": "google_scholar", "status": "disable"},
        {"name": "google_trend", "status": "disable"},
        {"name": "asknews", "status": "disable"},
        {"name": "reddit", "status": "disable"},
        {"name": "searx", "status": "disable"},
        {"name": "openweather", "status": "disable"},
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
        llm = LLMModel(
            name="Claude Sonet 4.5",
            region="ap-southeast-1",
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            model_max_tokens="4096",
            model_temperature="0.7",
            system_prompt=PromptFactory.load_llm_prompt()
        )
        session.add(llm)
        await session.commit()
        logger.info("✅ LLMs seeded successfully")

async def seed_agent(session):
    """Initialize default agent."""
    result = await session.execute(select(AgentModel))
    existing_agents = result.scalars().all()

    if not existing_agents:
        # Get first LLM
        sql_llm = await session.execute(select(LLMModel))
        llm = sql_llm.scalars().first()

        # Get enabled tools
        sql_tools = await session.execute(
            select(ToolModel).where(ToolModel.status == "enable")
        )
        enabled_tools = sql_tools.scalars().all()

        # Convert tools → [{"id":1,"name":"duckduckgo"}, ...]
        tool_list = [{"id": t.id, "name": t.name} for t in enabled_tools]

        agent = AgentModel(
            name="Yang-Agent",
            llm_id=llm.id,
            system_prompt=PromptFactory.load_agent_prompt(),
            tools=tool_list,
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