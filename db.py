from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://3MBao1g1oFnRE9J.root:q61xqCz3YFtkKYRy@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test?ssl_ca=isrgrootx1.pem&ssl_verify_cert=true&ssl_verify_identity=true"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl":{
            "ca": "isrgrootx1.pem",
        }
    },
    )
Sessionlocal = sessionmaker(bind=engine)
Base = declarative_base()