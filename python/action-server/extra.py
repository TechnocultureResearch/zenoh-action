import zenoh

zenoh.init_logger()
session = zenoh.open(config)



            


q1 = session.declare_queryable('Genotyper/1/DNAsensor/1/trigger')
