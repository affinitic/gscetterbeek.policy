from cirb.organizations import ORMBase
from cirb.organizations.content.organization import Address, Category, InCharge, Organization, Contact, Association
from zope import component
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig import Session
import transaction

from zope.interface import alsoProvides
from cirb.organizations.browser.interfaces import ISearch

def setupOrganizations(context):
    logger = context.getLogger("setupOrganization")
    logger.info('start setup organization')
    if context.readDataFile('cirb.organizations.txt') is None:
        return
    site = context.getSite()
    portal_workflow = site.portal_workflow

    ORGAFR = 'organizationfr'
    ORGANL = 'organizationnl'
    if not site.hasObject(ORGAFR):
        site.invokeFactory(type_name='Folder',
                id=ORGAFR,
                title="Organisme",
                description="",
                language="fr")
        orgafr = getattr(site, ORGAFR)
        #orgafr.setExcludeFromNav(True)
        alsoProvides(orgafr, ISearch)
        portal_workflow.doActionFor(orgafr,'publish')

        site.invokeFactory(type_name='Folder',
                id=ORGANL,
                title="Organisme",
                description="",
                language="nl")
        organl = getattr(site, ORGANL)
        #organl.setExcludeFromNav(True)
        alsoProvides(organl, ISearch)
        portal_workflow.doActionFor(organl,'publish')
        organl.addTranslationReference(orgafr)


        news = site.news
        news.setExcludeFromNav(True)
        news.reindexObject()

        events = site.events
        events.setExcludeFromNav(True)
        events.reindexObject()

        Members = site.Members
        Members.setExcludeFromNav(True)
        Members.reindexObject()

    add_test_organisations_in_db(logger)
    logger.info('end setup organization')


def add_test_organisations_in_db(logger):
    # TODO check if table exists
    engine = component.getUtility(IEngineFactory, name="gscetterbeek")()
    ORMBase.metadata.create_all(engine)

    session = Session()
    if len(session.query(Organization).all()) < 1:

        addr = Address(street='avenue des arts', num='21', post_code='1000', municipality='Bruxelles')
        cat = Category(music=True, welcome=True, other="god")
        incharge = InCharge(title="Sir", first_name="Benoit", second_name="Suttor")
        contact_addr = Address(street='contact street', num='7', post_code='1001', municipality='Brux')
        contact = Contact(title="Monsieur", first_name="James", second_name="Bond", phone="007/11.11.11", fax="00", email="jb@mi6.uk", address=contact_addr)
        # TODO add logo
        orga = Organization(name='CIRB', 
                address=addr, 
                person_incharge=incharge,
                person_contact=contact, 
                category=cat, 
                status="asbl", 
                language="fr", 
                website="http://www.cirb.irisnet.be",
                x="150041",
                y="170633")
        addr2 = Address(street='kunststraat', num='21', post_code='1000', municipality='Brussel')
        cat2 = Category(music=True, welcome=True, other="god")
        incharge2 = InCharge(title="Sir", first_name="Benoit", second_name="Suttor")
        contact_addr2 = Address(street='contact street', num='7', post_code='1000', municipality='Brux')
        contact2 = Contact(title="double zero", first_name="Bond", second_name="James", phone="007/11.11.11", fax="00", email="jb@mi6.uk", address=contact_addr2)

        orga2 = Organization(name='CIBG', 
                address=addr2, 
                person_incharge=incharge2,
                person_contact=contact2, 
                category=cat2, 
                status="asbl", 
                language="nl", 
                website="http://www.cibg.irisnet.be",
                x="150041",
                y="170633")

        session.add(orga)
        session.add(orga2)
        session.flush()

        assoc = Association(association_type = "lang")
        assoc.translated_id = orga2.organization_id
        assoc.canonical_id = orga.organization_id 
        session.add(assoc)
        transaction.commit()
    else:
        logger.info('There are already some organizations in DB.')
